from __future__ import annotations

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.query_routes import create_query_router
from app.query.in_memory import InMemoryEvidenceRepository
from app.query.models import EvidenceQueryRequest
from app.query.service import EvidenceQueryService
from app.repo.inmemory import InMemoryGraphRepo


def populated_service() -> EvidenceQueryService:
    graph = InMemoryGraphRepo()
    graph.merge_node("ev-1", ["EVIDENCE"], {"event_id": "event-1", "evidence_type": "login", "source": "events", "timestamp": "2026-07-15T10:00:00+00:00", "confidence": 0.9})
    graph.merge_node("user-1", ["USER"], {"id": "u-1"})
    graph.merge_relationship("user-1", "ev-1", "OBSERVED", {"source": "evidence-service"})
    return EvidenceQueryService(InMemoryEvidenceRepository(graph))


def test_repository_reads_processed_data_without_processing():
    service = populated_service()
    evidence = service.get_evidence("ev-1")
    assert evidence is not None
    assert evidence.evidence_type == "login"
    assert service.get_by_entity("user-1")[0].evidence_id == "ev-1"
    assert service.get_relationships("ev-1")[0].relationship_type == "OBSERVED"
    assert service.get_metadata("ev-1").source == "events"
    assert service.validate("ev-1").valid is True
    assert service.statistics().total_evidence == 1


def test_query_search_and_timeline_are_read_only():
    service = populated_service()
    result = service.search(EvidenceQueryRequest(query="login", start_time="2026-07-15T09:00:00+00:00"))
    assert result.total == 1
    timeline = service.get_timeline(EvidenceQueryRequest(evidence_type="login"))
    assert timeline.items[0].evidence_id == "ev-1"


def test_query_api_exposes_read_only_endpoints():
    app = FastAPI()
    app.include_router(create_query_router(populated_service()))
    client = TestClient(app)

    assert client.get("/api/v1/evidence/ev-1").status_code == 200
    assert client.get("/api/v1/evidence/ev-1/metadata").json()["evidence_id"] == "ev-1"
    assert client.get("/api/v1/evidence/ev-1/validation").json()["valid"] is True
    assert client.get("/api/v1/evidence/entity/user-1").status_code == 200
    assert client.get("/api/v1/evidence/ev-1/relationships").json()["relationships"][0]["relationship_type"] == "OBSERVED"
    assert client.post("/api/v1/evidence/search", json={"query": "login"}).json()["total"] == 1
    assert client.get("/api/v1/evidence/statistics").json()["total_evidence"] == 1

    # The query surface is read-only; unsupported write methods are not registered.
    assert client.post("/api/v1/evidence/ev-1", json={}).status_code == 405
