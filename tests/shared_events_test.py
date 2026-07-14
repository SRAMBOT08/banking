import json
from uuid import UUID
from datetime import datetime

from sentineliq_shared.events.base import BaseEvent
from sentineliq_shared.enums.types import EventType, Severity


def test_base_event_serialization():
    ev = BaseEvent(
        event_type=EventType.TRANSACTION,
        event_version="1.0",
        tenant_id="tenant-123",
        source_id="source-abc",
        producer_service="ingestion-service",
    )

    d = ev.to_dict()
    assert "event_id" in d
    assert d["event_type"] == EventType.TRANSACTION.value

    j = ev.to_json()
    assert isinstance(j, str)

    ev2 = BaseEvent.from_json(j)
    assert isinstance(ev2.event_id, UUID)
    assert ev2.tenant_id == "tenant-123"
