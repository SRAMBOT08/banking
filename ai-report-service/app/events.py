from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path
from typing import Awaitable, Callable
from uuid import NAMESPACE_URL, uuid5

from confluent_kafka import Consumer, KafkaError, Producer

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from shared.sentineliq_shared.events.autonomous import CaseCreatedEvent, ReportGeneratedEvent


class ReportEventPublisher:
    def __init__(self, bootstrap: str, topic: str):
        self.topic = topic
        self.producer = Producer({"bootstrap.servers": bootstrap})

    def publish(self, event: ReportGeneratedEvent) -> None:
        self.producer.produce(self.topic, key=event.case_id.encode(), value=event.model_dump_json().encode())
        self.producer.poll(0)
        self.producer.flush(5)


class CaseCreatedConsumer:
    def __init__(self, bootstrap: str, topic: str, group: str, dlq_topic: str,
                 handler: Callable[[CaseCreatedEvent], Awaitable[None]], attempts: int = 3):
        self.handler, self.topic, self.dlq_topic, self.attempts = handler, topic, dlq_topic, attempts
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
                    event = CaseCreatedEvent.model_validate_json(message.value())
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


def report_event(report, source: CaseCreatedEvent, producer_service: str) -> ReportGeneratedEvent:
    report_id = str(report.report_id)
    return ReportGeneratedEvent(
        event_id=uuid5(NAMESPACE_URL, f"report-generated|{report_id}"),
        tenant_id=source.tenant_id,
        correlation_id=source.correlation_id,
        investigation_id=source.investigation_id,
        workflow_id=source.workflow_id,
        trace_id=source.trace_id,
        source_id=source.event_id.hex,
        producer_service=producer_service,
        idempotency_key=f"report-generated:{report_id}",
        report_id=report_id,
        case_id=str(report.case_id),
        case_version=report.case_version,
        report_type=str(report.report_type),
        report_format=str(report.output_format),
        report=report.model_dump(mode="json"),
        case_file=source.case_file,
        source_hash=report.source_hash,
    )
