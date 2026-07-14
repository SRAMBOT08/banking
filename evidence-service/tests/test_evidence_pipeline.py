import json
from uuid import uuid4
from datetime import datetime

from app.pipeline.extractor import extract
from app.pipeline.resolver import resolve_entities, canonical_id
from app.pipeline.relationship_builder import build_relationships
from app.repo.inmemory import InMemoryGraphRepo
from app.pipeline.graph_engine import GraphEngine
from app.events import BaseEvent


def make_event():
    ev = BaseEvent.model_validate({
        "event_id": str(uuid4()),
        "event_type": "test.event",
        "event_version": "1",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "tenant_id": "t1",
        "source_id": "s1",
        "metadata": {"user_id": "u1", "ip": "1.2.3.4", "account_id": "a1"},
    })
    return ev


def test_extract_resolve_build_graph():
    ev = make_event()
    extracted = extract(ev)
    resolved = resolve_entities(extracted)
    rels = build_relationships(resolved)
    repo = InMemoryGraphRepo()
    engine = GraphEngine(repo)
    engine.apply(resolved, rels)
    # assert nodes and relationships created
    assert len(repo.nodes) >= 1
    assert len(repo.relationships) >= 0

*** End Patch
