from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path
from typing import Any, Awaitable, Callable
from uuid import NAMESPACE_URL, uuid5

from confluent_kafka import Consumer, KafkaError, Producer

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from shared.sentineliq_shared.events.autonomous import CaseCreatedEvent, InvestigationCompletedEvent


class CaseEventPublisher:
    def __init__(self, bootstrap: str, topic: str):
        self.topic = topic
        self.producer = Producer({"bootstrap.servers": bootstrap})

    def publish(self, event: CaseCreatedEvent) -> None:
        key = event.case_id.encode()
        self.producer.produce(self.topic, key=key, value=event.model_dump_json().encode())
        self.producer.poll(0)
        self.producer.flush(5)


class CompletedInvestigationConsumer:
    def __init__(self, bootstrap: str, topic: str, group: str, dlq_topic: str,
                 handler: Callable[[InvestigationCompletedEvent], Awaitable[None]], attempts: int = 3):
        self.handler, self.topic, self.dlq_topic = handler, topic, dlq_topic
        self.attempts = attempts
        self.consumer = Consumer({"bootstrap.servers": bootstrap, "group.id": group,
                                  "auto.offset.reset": "earliest", "enable.auto.commit": False})
        self.dlq = Producer({"bootstrap.servers": bootstrap})
        self.running = False
        self.task: asyncio.Task | None = None

    def start(self) -> None:
        self.consumer.subscribe([self.topic])
        self.running = True
        self.task = asyncio.create_task(self._poll())

    async def _poll(self) -> None:
        loop = asyncio.get_running_loop()
        while self.running:
            message = await loop.run_in_executor(None, self.consumer.poll, 1.0)
            if message is None:
                continue
            if message.error():
                if message.error().code() != KafkaError._PARTITION_EOF:
                    continue
                continue
            for attempt in range(1, self.attempts + 1):
                try:
                    event = InvestigationCompletedEvent.model_validate_json(message.value())
                    await self.handler(event)
                    self.consumer.commit(message=message, asynchronous=False)
                    break
                except Exception:
                    if attempt == self.attempts:
                        self.dlq.produce(self.dlq_topic, key=message.key(), value=message.value())
                        self.dlq.flush(5)
                        self.consumer.commit(message=message, asynchronous=False)
                    else:
                        await asyncio.sleep(2 ** (attempt - 1))

    async def stop(self) -> None:
        self.running = False
        if self.task:
            self.task.cancel()
        self.consumer.close()


def case_event(case_file: Any, source: InvestigationCompletedEvent, producer_service: str) -> CaseCreatedEvent:
    case_id = str(case_file.case_id)
    version = int(case_file.version.version)
    event_id = uuid5(NAMESPACE_URL, f"case-created|{case_id}|{version}")
    return CaseCreatedEvent(
        event_id=event_id,
        tenant_id=source.tenant_id,
        correlation_id=source.correlation_id,
        investigation_id=source.investigation_id,
        workflow_id=source.workflow_id,
        trace_id=source.trace_id,
        source_id=source.event_id.hex,
        producer_service=producer_service,
        idempotency_key=f"case-created:{case_id}:{version}",
        case_id=case_id,
        case_version=version,
        case_file=case_file.model_dump(mode="json"),
    )
