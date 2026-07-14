from __future__ import annotations

import asyncio
import json
from typing import Any, Awaitable, Callable

from confluent_kafka import Consumer, KafkaError, Producer

from app.config import AdapterSettings


class AdapterEventPublisher:
    def __init__(self, settings: AdapterSettings):
        self.settings = settings
        self.producer = Producer({"bootstrap.servers": settings.kafka_bootstrap_servers}) if settings.kafka_bootstrap_servers else None

    def publish(self, topic: str, key: str, payload: dict[str, Any]) -> None:
        if not self.producer:
            return
        self.producer.produce(topic, key=key.encode(), value=json.dumps(payload, sort_keys=True).encode())
        self.producer.poll(0)
        self.producer.flush(5)

    def publish_started(self, payload: dict[str, Any], key: str) -> None:
        self.publish(self.settings.execution_started_topic, key, payload)

    def publish_completed(self, payload: dict[str, Any], key: str) -> None:
        self.publish(self.settings.execution_completed_topic, key, payload)

    def publish_failed(self, payload: dict[str, Any], key: str) -> None:
        self.publish(self.settings.execution_failed_topic, key, payload)

    def publish_verified(self, payload: dict[str, Any], key: str) -> None:
        self.publish(self.settings.execution_verified_topic, key, payload)


class ReadyTaskConsumer:
    def __init__(self, settings: AdapterSettings, handler: Callable[[dict[str, Any]], Awaitable[None]]):
        self.settings = settings
        self.handler = handler
        self.consumer = Consumer(
            {
                "bootstrap.servers": settings.kafka_bootstrap_servers,
                "group.id": settings.kafka_consumer_group,
                "auto.offset.reset": "earliest",
            }
        )
        self.running = False
        self.task: asyncio.Task | None = None

    def start(self) -> None:
        self.running = True
        self.consumer.subscribe([self.settings.execution_ready_topic])
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
            payload = json.loads(message.value().decode())
            await self.handler(payload)

    async def stop(self) -> None:
        self.running = False
        if self.task:
            self.task.cancel()
        self.consumer.close()
