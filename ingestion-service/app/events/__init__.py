# thin wrappers importing shared events package
from sentineliq_shared.events.base import BaseEvent
from sentineliq_shared.events.registry import EventRegistry, DuplicateEventRegistrationError
from sentineliq_shared.events.serialization import serialize_event, deserialize_event


def _register_default_events() -> None:
	for event_type in ("authentication", "transaction", "threat", "identity", "asset", "fraud", "evidence"):
		try:
			EventRegistry.register_event(event_type, "1.0", BaseEvent)
		except DuplicateEventRegistrationError:
			continue


_register_default_events()
