from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path
from typing import Awaitable, Callable

from confluent_kafka import Consumer, KafkaError, Producer

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from shared.sentineliq_shared.events.autonomous import ReportGeneratedEvent


class ReportGeneratedConsumer:
    def __init__(self, settings, handler: Callable[[dict], Awaitable[None]]):
        self.settings, self.handler = settings, handler
        self.consumer = Consumer({"bootstrap.servers": settings.kafka_bootstrap,
                                  "group.id": settings.consumer_group,
                                  "auto.offset.reset": "earliest", "enable.auto.commit": False})
        self.dlq = Producer({"bootstrap.servers": settings.kafka_bootstrap})
        self.running = False
        self.task: asyncio.Task | None = None

    def start(self) -> None:
        self.consumer.subscribe([self.settings.report_generated_topic])
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
            for attempt in range(1, 4):
                try:
                    event = ReportGeneratedEvent.model_validate_json(message.value())
                    await self.handler(event.model_dump(mode="json"))
                    self.consumer.commit(message=message, asynchronous=False)
                    break
                except Exception:
                    if attempt == 3:
                        self.dlq.produce(self.settings.report_dlq_topic, key=message.key(), value=message.value())
                        self.dlq.flush(5)
                        self.consumer.commit(message=message, asynchronous=False)
                    else:
                        await asyncio.sleep(2 ** (attempt - 1))

    async def stop(self) -> None:
        self.running = False
        if self.task:
            self.task.cancel()
        self.consumer.close()
