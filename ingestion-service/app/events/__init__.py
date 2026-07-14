# thin wrappers importing shared events package
from sentineliq_shared.events.base import BaseEvent
from sentineliq_shared.events.registry import EventRegistry
from sentineliq_shared.events.serialization import serialize_event, deserialize_event
