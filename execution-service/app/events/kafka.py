from __future__ import annotations

import asyncio
import json
from typing import Awaitable, Callable

from confluent_kafka import Consumer, KafkaError

from app.config.settings import Settings


class CompletedInvestigationConsumer:
    def __init__(self, settings: Settings, handler: Callable[[dict], Awaitable[None]]):
        self.settings = settings
        self.handler = handler
        self.consumer = Consumer(
            {
                "bootstrap.servers": settings.kafka_bootstrap,
                "group.id": settings.consumer_group,
                "auto.offset.reset": "earliest",
            }
        )
        self.running = False
        self.task: asyncio.Task | None = None

    def start(self) -> None:
        self.consumer.subscribe([self.settings.investigation_completed_topic])
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
            await self.handler(json.loads(message.value().decode()))

    async def stop(self) -> None:
        self.running = False
        if self.task:
            self.task.cancel()
        self.consumer.close()
