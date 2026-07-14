from __future__ import annotations
import asyncio
import json
from typing import Awaitable, Callable
from confluent_kafka import Consumer, Producer, KafkaError
from app.config.settings import Settings


class KafkaPublisher:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.producer = Producer({"bootstrap.servers": settings.kafka_bootstrap})

    def publish(self, topic: str, payload: dict, key: str) -> None:
        self.producer.produce(topic, key=key.encode(), value=json.dumps(payload, sort_keys=True).encode())
        self.producer.poll(0)
        self.producer.flush(5)


class SnapshotEventConsumer:
    def __init__(self, settings: Settings, handler: Callable[[dict], Awaitable[None]]):
        self.settings = settings
        self.handler = handler
        self.consumer = Consumer({"bootstrap.servers": settings.kafka_bootstrap, "group.id": settings.consumer_group, "auto.offset.reset": "earliest"})
        self.running = False
        self.task: asyncio.Task | None = None

    def start(self) -> None:
        self.consumer.subscribe([self.settings.snapshot_topic])
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
