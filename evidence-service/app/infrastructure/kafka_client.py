from __future__ import annotations

import asyncio
from typing import Callable, Optional
from confluent_kafka import Consumer, KafkaError, Producer
from app.config.settings import settings
from app.core.logger import get_logger

logger = get_logger("kafka_client")


class KafkaEventPublisher:
    """Output boundary for versioned evidence events."""

    def __init__(self, bootstrap: Optional[str] = None):
        self._producer = Producer({"bootstrap.servers": bootstrap or settings.kafka_bootstrap})

    def publish(self, topic: str, value: bytes, key: Optional[bytes] = None):
        self._producer.produce(topic, key=key, value=value)
        self._producer.poll(0)
        self._producer.flush(5)
        logger.info("kafka_published", extra={"topic": topic})


class KafkaConsumerWrapper:
    def __init__(self, topic: str, group_id: Optional[str] = None, bootstrap: Optional[str] = None,
                 dlq_topic: Optional[str] = None, max_attempts: int = 3):
        conf = {
            "bootstrap.servers": bootstrap or settings.kafka_bootstrap,
            "group.id": group_id or settings.consumer_group,
            "auto.offset.reset": "earliest",
            "enable.auto.commit": False,
        }
        self._consumer = Consumer(conf)
        self._topic = topic
        self._running = False
        self._dlq_topic = dlq_topic
        self._max_attempts = max_attempts
        self._producer = Producer({"bootstrap.servers": bootstrap or settings.kafka_bootstrap}) if dlq_topic else None

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
                for attempt in range(1, self._max_attempts + 1):
                    try:
                        await message_handler(msg)
                        self._consumer.commit(message=msg, asynchronous=False)
                        break
                    except Exception as exc:
                        logger.error("message_attempt_failed", extra={"topic": self._topic,
                                                                       "attempt": attempt,
                                                                       "error": str(exc)})
                        if attempt == self._max_attempts:
                            if self._producer and self._dlq_topic:
                                self._producer.produce(self._dlq_topic, key=msg.key(), value=msg.value())
                                self._producer.flush(5)
                            self._consumer.commit(message=msg, asynchronous=False)
                        else:
                            await asyncio.sleep(2 ** (attempt - 1))

        asyncio.create_task(_poll_loop())

    def stop(self):
        self._running = False
        try:
            self._consumer.close()
        except Exception:
            pass
