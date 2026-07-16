from __future__ import annotations
from threading import Lock
from typing import Protocol
from .models import SimulationEvent
from .config import settings


class EventPublisher(Protocol):
    def publish(self, event: SimulationEvent) -> None: ...
    def flush(self) -> None: ...


class InMemoryPublisher:
    """Thread-safe local transport used for replay, demos, and unit tests."""
    def __init__(self): self.events: list[SimulationEvent] = []; self._lock = Lock()
    def publish(self, event: SimulationEvent) -> None:
        with self._lock: self.events.append(event)
    def flush(self) -> None: pass


class KafkaEventPublisher:
    def __init__(self, bootstrap_servers: str | None = None, topic: str | None = None):
        from confluent_kafka import Producer
        self.topic = topic or settings.event_topic
        self.producer = Producer({'bootstrap.servers': bootstrap_servers or settings.kafka_bootstrap_servers})
    def publish(self, event: SimulationEvent) -> None:
        self.producer.produce(self.topic, key=str(event.event_id).encode(), value=event.model_dump_json().encode(), headers=[('event-type', event.event_type.value.encode())])
        self.producer.poll(0)
    def flush(self) -> None: self.producer.flush(10)


def publisher_from_settings() -> EventPublisher:
    return KafkaEventPublisher() if settings.transport.lower() == 'kafka' else InMemoryPublisher()
