from __future__ import annotations

import asyncio
from typing import Callable, Optional
from confluent_kafka import Consumer, KafkaError
from app.config.settings import settings
from app.core.logger import get_logger

logger = get_logger("kafka_client")


class KafkaConsumerWrapper:
    def __init__(self, topic: str, group_id: Optional[str] = None, bootstrap: Optional[str] = None):
        conf = {
            "bootstrap.servers": bootstrap or settings.kafka_bootstrap,
            "group.id": group_id or f"evidence-{topic}-group",
            "auto.offset.reset": "earliest",
        }
        self._consumer = Consumer(conf)
        self._topic = topic
        self._running = False

    def start(self, message_handler: Callable):
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
                await message_handler(msg)

        asyncio.create_task(_poll_loop())

    def stop(self):
        self._running = False
        try:
            self._consumer.close()
        except Exception:
            pass
