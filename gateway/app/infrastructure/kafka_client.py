from __future__ import annotations

from typing import Optional
from confluent_kafka import Producer
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
