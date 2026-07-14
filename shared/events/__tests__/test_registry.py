import pytest

from sentineliq_shared.events.registry import EventRegistry, DuplicateEventRegistrationError, UnknownEventError
from sentineliq_shared.events.base import BaseEvent


class DummyEvent(BaseEvent):
    pass


def test_event_registry_register_and_lookup():
    EventRegistry._registry.clear()
    EventRegistry.register_event("dummy", "1.0", DummyEvent)
    model = EventRegistry.get_event("dummy", "1.0")
    assert model is DummyEvent


def test_duplicate_registration_raises():
    EventRegistry._registry.clear()
    EventRegistry.register_event("x", "1.0", DummyEvent)
    with pytest.raises(DuplicateEventRegistrationError):
        EventRegistry.register_event("x", "1.0", DummyEvent)


def test_unknown_event_raises():
    EventRegistry._registry.clear()
    with pytest.raises(UnknownEventError):
        EventRegistry.get_event("missing", "1.0")
