from __future__ import annotations

from typing import Optional

from app.infrastructure.kafka_client import KafkaProducerWrapper
from app.events import serialize_event
from app.config.settings import settings
from app.core.logger import get_logger

logger = get_logger("publisher")


class Publisher:
    def __init__(self, producer: Optional[KafkaProducerWrapper] = None):
        self.producer = producer or KafkaProducerWrapper()

    def publish_normalized(self, event) -> None:
        try:
            payload = serialize_event(event)
            self.producer.produce(settings.normalized_topic, key=str(event.event_id).encode(), value=payload)
            logger.info("published", extra={"topic": settings.normalized_topic, "event_id": str(event.event_id)})
        except Exception as exc:
            logger.error("publish_failed", extra={"error": str(exc)})
            raise
