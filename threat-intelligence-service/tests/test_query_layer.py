from __future__ import annotations

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.query_routes import create_query_router
from app.knowledge_registry.manager import RegistryManager
from app.query.in_memory import InMemoryThreatRepository
from app.query.models import ThreatSearchRequest
from app.query.service import ThreatQueryService
from app.repositories.candidates_repo import InMemoryCandidatesRepo


def make_service(tmp_path):
    (tmp_path / "account_takeover-1.yaml").write_text(
        "name: account_takeover\nversion: '1'\nnodes: []\nedges: []\n",
        encoding="utf-8",
    )
    registry = RegistryManager(str(tmp_path))
    registry.load()
    candidates = InMemoryCandidatesRepo()
    candidates.save({
        "candidate_id": "threat-1",
        "investigation_id": "investigation-1",
        "correlation_id": "correlation-1",
        "tenant_id": "tenant-1",
        "pattern_name": "account_takeover",
        "pattern_version": "1",
        "confidence": 87,
        "explanation": {"reason": "stored match", "missing_evidence": [{"type": "device"}]},
        "evidence_refs": [{"id": "ev-1"}],
        "timestamp": "2026-07-15T10:00:00Z",
    })
    return ThreatQueryService(InMemoryThreatRepository(registry, candidates))


def test_repository_reads_processed_threats_and_registry(tmp_path):
    service = make_service(tmp_path)
    threat = service.find_threat("threat-1")
    assert threat is not None
    assert threat.confidence == 87
    assert threat.missing_evidence == [{"type": "device"}]
    assert service.find_pattern("account_takeover").name == "account_takeover"
    assert service.search(ThreatSearchRequest(investigation_id="investigation-1")).total == 1
    assert service.statistics().threat_count == 1
    assert service.metadata().candidate_count == 1


def test_threat_query_api_is_read_only(tmp_path):
    app = FastAPI()
    app.include_router(create_query_router(make_service(tmp_path)))
    client = TestClient(app)

    assert client.get("/api/v1/threat/threat-1").json()["pattern_name"] == "account_takeover"
    assert client.get("/api/v1/threat/pattern/account_takeover").status_code == 200
    assert client.post("/api/v1/threat/search", json={"min_confidence": 80}).json()["total"] == 1
    assert client.get("/api/v1/threat/statistics").json()["threat_count"] == 1
    assert client.post("/api/v1/threat/threat-1", json={}).status_code == 405
