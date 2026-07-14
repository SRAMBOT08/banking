from __future__ import annotations
import asyncio
from typing import Callable, Optional
from confluent_kafka import Consumer, KafkaError, Producer
from app.config.settings import settings
from app.core.logger import get_logger
from app.models.events import InvestigationEvent, snapshot_metadata_event

logger = get_logger("investigation_kafka")


class KafkaProducer:
    def __init__(self):
        self.producer = Producer({"bootstrap.servers": settings.kafka_bootstrap})

    def publish(self, topic: str, value: bytes, key: Optional[bytes] = None):
        self.producer.produce(topic, key=key, value=value)
        self.producer.poll(0)
        self.producer.flush(5)
        logger.info("kafka_published", extra={"topic": topic})

    def publish_investigation(self, topic: str, event_type: str, investigation, timestamp: str, key: Optional[bytes] = None):
        event = InvestigationEvent.from_investigation(event_type, investigation, timestamp)
        self.publish(topic, event.model_dump_json().encode(), key or investigation.investigation_id.encode())

    def publish_snapshot(self, topic: str, snapshot):
        event = snapshot_metadata_event(snapshot)
        self.publish(topic, event.model_dump_json().encode(), snapshot.metadata.investigation_id.encode())
        logger.info("snapshot_published", extra={"investigation_id": snapshot.metadata.investigation_id,
                                                   "snapshot_version": snapshot.metadata.snapshot_version,
                                                   "topic": topic})


class KafkaConsumer:
    def __init__(self, topic: str, group_id: str):
        self.consumer = Consumer({"bootstrap.servers": settings.kafka_bootstrap, "group.id": group_id, "auto.offset.reset": "earliest"})
        self.topic = topic
        self.running = False

    def start(self, handler: Callable):
        self.consumer.subscribe([self.topic])
        self.running = True

        async def poll_loop():
            loop = asyncio.get_event_loop()
            while self.running:
                message = await loop.run_in_executor(None, self.consumer.poll, 1.0)
                if message is None:
                    continue
                if message.error():
                    if message.error().code() != KafkaError._PARTITION_EOF:
                        logger.error("kafka_error", extra={"error": str(message.error())})
                    continue
                await handler(message)

        asyncio.create_task(poll_loop())

    def stop(self):
        self.running = False
        self.consumer.close()
