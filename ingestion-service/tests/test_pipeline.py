import asyncio
import json
from datetime import datetime
from uuid import uuid4

import pytest

from app.pipeline.validator import validate_raw_message, ValidationError
from app.pipeline.normalizer import normalize
from app.pipeline.enricher import enrich
from app.pipeline.deduper import Deduper, InMemoryDedupeStore
from app.pipeline.publisher import Publisher
from app.pipeline.orchestrator import PipelineOrchestrator
from app.events import BaseEvent


def make_raw_event():
    ev = {
        "event_id": str(uuid4()),
        "event_type": "test.event",
        "event_version": "1",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "tenant_id": "tenant_1",
        "source_id": "source_1",
        "metadata": {},
    }
    return json.dumps(ev).encode()


def test_validate_and_normalize_success():
    raw = make_raw_event()
    payload_dict, model = validate_raw_message(raw)
    assert payload_dict["event_type"] == "test.event"
    ev = normalize(payload_dict, raw)
    assert isinstance(ev, BaseEvent)


def test_validation_failure_missing_fields():
    raw = json.dumps({"foo": "bar"}).encode()
    with pytest.raises(ValidationError):
        validate_raw_message(raw)


@pytest.mark.asyncio
async def test_dedup_and_orchestration():
    raw = make_raw_event()
    # in-memory store
    store = InMemoryDedupeStore()
    deduper = Deduper(store, window_seconds=1)
    publisher = Publisher()
    orchestrator = PipelineOrchestrator(deduper, publisher)

    ev = await orchestrator.handle_message(raw)
    assert ev.event_type == "test.event"

    # second time should be duplicate
    with pytest.raises(Exception):
        await orchestrator.handle_message(raw)

*** End Patch
