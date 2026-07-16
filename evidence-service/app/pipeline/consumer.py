from __future__ import annotations

import asyncio
from typing import Callable

from confluent_kafka import Consumer, KafkaError
from app.core.logger import get_logger
from app.config import settings

logger = get_logger("consumer")


class KafkaConsumerStub:
    def __init__(self, bootstrap: str = None, group: str = None):
        # lightweight stub — in real deploy use confluent_kafka.Consumer
        self._running = False

    def start(self, topic: str, handler: Callable):
        # Not implemented: wiring to Kafka. Tests will call handler directly.
        self._running = True
        logger.info("consumer_stub_started", extra={"topic": topic})

    def stop(self):
        self._running = False
