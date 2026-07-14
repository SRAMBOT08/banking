from __future__ import annotations
from typing import Optional, Callable
import asyncio
from confluent_kafka import Producer, Consumer, KafkaError
from app.config.settings import settings
from app.core.logger import get_logger

logger = get_logger("kafka_client")


class KafkaProducerWrapper:
    def __init__(self, bootstrap_servers: Optional[str] = None):
        self._producer = Producer({"bootstrap.servers": bootstrap_servers or settings.kafka_bootstrap})

    def produce(self, topic: str, key: Optional[bytes], value: bytes, headers: Optional[list] = None):
        def delivery(err, msg):
            if err:
                logger.error("delivery_failed", extra={"error": str(err), "topic": topic})
            else:
                logger.debug("delivered", extra={"topic": msg.topic(), "partition": msg.partition(), "offset": msg.offset()})

        self._producer.produce(topic, key=key, value=value, headers=headers, callback=delivery)
        self._producer.poll(0)

    def flush(self, timeout: int = 5):
        self._producer.flush(timeout)


class KafkaConsumerWrapper:
    def __init__(self, topic: str, group_id: Optional[str] = None, bootstrap: Optional[str] = None):
        conf = {"bootstrap.servers": bootstrap or settings.kafka_bootstrap,
                "group.id": group_id or "attack-knowledge-group",
                "auto.offset.reset": "earliest"}
        self._consumer = Consumer(conf)
        self._topic = topic
        self._running = False

    def start(self, handler: Callable):
        self._consumer.subscribe([self._topic])
        self._running = True

        async def _poll_loop():
            loop = asyncio.get_event_loop()
            while self._running:
                msg = await loop.run_in_executor(None, self._consumer.poll, 1.0)
                if msg is None:
                    await asyncio.sleep(0.1)
                    continue
                if msg.error():
                    if msg.error().code() == KafkaError._PARTITION_EOF:
                        continue
                    logger.error("kafka_error", extra={"error": str(msg.error())})
                    continue
                await handler(msg)

        asyncio.create_task(_poll_loop())

    def stop(self):
        self._running = False
        try:
            self._consumer.close()
        except Exception:
            pass
