from __future__ import annotations

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.query_routes import create_query_router
from app.query.in_memory import InMemoryInvestigationMemoryRepository
from app.query.models import InvestigationSearchRequest, SimilarityRequest
from app.query.service import InvestigationMemoryQueryService
from app.write.snapshot_builder import IncompleteInvestigationError, InvestigationSnapshotBuilder


def service():
    return InvestigationMemoryQueryService(InMemoryInvestigationMemoryRepository())


def test_repository_retrieves_completed_snapshots_and_historical_artifacts():
    query = service()
    record = query.lookup("investigation-history-001")
    assert record and record.completed
    assert record.snapshot.outcome.success
    assert query.outcome("investigation-history-001").outcome_type.value == "account_protected"
    assert query.resolution("investigation-history-001").success_rate == 1.0
    assert query.lessons("investigation-history-001").lessons
    assert query.related("investigation-history-001")
    assert query.historical_evidence("investigation-history-001")[0].evidence_type == "authentication_event"
    assert query.historical_threat("investigation-history-001")
    assert query.historical_knowledge("investigation-history-001")
    assert query.historical_graph("investigation-history-001")


def test_similarity_timeline_and_statistics_are_deterministic():
    query = service()
    result = query.similarity(SimilarityRequest(investigation_id="new", evidence_types=["authentication_event"], threat_patterns=["Account Takeover"], mitre_mapping=["T1078"], fraud_category="account_takeover", confidence=0.9))
    assert result.matching_investigation_ids
    assert result.overall_score > 0.5
    timeline = query.timeline("account-001")
    assert timeline.timeline_type == "entity"
    assert timeline.events
    stats = query.statistics()
    assert stats.investigation_count == 3
    assert stats.attack_frequency["account_takeover"] == 2
    assert stats.resolution_success_rate > 0.0
    assert query.search(InvestigationSearchRequest(fraud_category="account_takeover")).total == 2


def test_memory_api_is_read_only():
    query = service()
    app = FastAPI()
    app.include_router(create_query_router(query))
    client = TestClient(app)
    assert client.get("/api/v1/memory/investigation/investigation-history-001").status_code == 200
    assert client.get("/api/v1/memory/similar/investigation-history-001").status_code == 200
    assert client.get("/api/v1/memory/timeline/account-001").status_code == 200
    assert client.get("/api/v1/memory/statistics").json()["investigation_count"] == 3
    assert client.get("/api/v1/memory/outcome/investigation-history-001").status_code == 200
    assert client.get("/api/v1/memory/resolution/investigation-history-001").status_code == 200
    assert client.get("/api/v1/memory/lessons/investigation-history-001").status_code == 200
    assert client.get("/api/v1/memory/related/investigation-history-001").status_code == 200
    assert client.post("/api/v1/memory/search", json={"fraud_category": "account_takeover"}).json()["total"] == 2
    assert client.post("/api/v1/memory/similarity", json={"threat_patterns": ["Account Takeover"]}).status_code == 200
    assert client.post("/api/v1/memory/investigation/investigation-history-001", json={}).status_code == 405
    assert client.get("/api/v1/memory/investigation/unknown").status_code == 404


def test_snapshot_builder_stores_completed_case_intelligence_only():
    snapshot = InvestigationSnapshotBuilder().build({"investigation_id": "completed-1", "tenant_id": "tenant-1", "workflow_status": "COMPLETED", "evidence": [{"evidence_id": "e-1", "evidence_type": "authentication_event"}], "metadata": {"outcome_type": "account_protected", "outcome_success": True}})
    assert snapshot.summary.investigation_id == "completed-1"
    assert snapshot.evidence_references[0].evidence_id == "e-1"
    with __import__("pytest").raises(IncompleteInvestigationError):
        InvestigationSnapshotBuilder().build({"investigation_id": "open-1", "tenant_id": "tenant-1", "workflow_status": "GRAPH_ANALYSIS"})
