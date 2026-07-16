from __future__ import annotations

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.query_routes import create_query_router
from app.query.in_memory import InMemoryKnowledgeRepository
from app.query.models import KnowledgeCategory, KnowledgeDetails, KnowledgeSearchRequest, KnowledgeTag
from app.query.service import KnowledgeQueryService
from app.providers.interfaces import ProviderRegistry


def service():
    return KnowledgeQueryService(InMemoryKnowledgeRepository())


def test_repository_supports_typed_lookups_search_relationships_and_versions():
    query = service()
    technique = query.find_technique("T1078")
    assert technique is not None
    assert technique.technique_id == "T1078"
    assert query.find_fraud_pattern("fraud.account_takeover").risk_score == 85
    assert query.find_control("AC-2").control_family == "Access Control"
    assert query.find_playbook("pb.account_takeover").steps
    result = query.search(KnowledgeSearchRequest(category=KnowledgeCategory.MITRE_TECHNIQUE))
    assert result.total == 1
    assert query.relationships("T1078")[0].target_id == "TA0001"
    assert len(query.versions("T1078")) == 2
    assert query.statistics().item_count >= 8
    assert query.metadata().provider_count == 1
    assert query.validate().valid


def test_search_supports_tags_keywords_and_relationship_types():
    query = service()
    assert query.search(KnowledgeSearchRequest(tags=["account_takeover"])).total >= 3
    assert query.search(KnowledgeSearchRequest(query="Valid Accounts")).items[0].id == "T1078"
    relation_search = query.search(KnowledgeSearchRequest(relationship_type="pattern_to_recommendation"))
    assert "fraud.account_takeover" in {item.id for item in relation_search.items}


def test_provider_registry_is_pluggable():
    class Provider:
        name = "custom"
        def items(self):
            return [KnowledgeDetails(id="custom-1", name="Custom Policy", category="policy", provider=self.name, tags=[KnowledgeTag(name="custom")])]
        def recommendations(self): return []
        def relationships(self): return []

    registry = ProviderRegistry([Provider()])
    repository = InMemoryKnowledgeRepository(registry)
    assert repository.find_item("custom-1").provider == "custom"


def test_knowledge_query_api_is_read_only():
    app = FastAPI()
    app.include_router(create_query_router(service()))
    client = TestClient(app)
    assert client.get("/api/v1/knowledge/T1078").status_code == 200
    assert client.get("/api/v1/knowledge/mitre/technique/T1078").json()["technique_id"] == "T1078"
    assert client.get("/api/v1/knowledge/fraud/fraud.account_takeover").status_code == 200
    assert client.get("/api/v1/knowledge/relationship/rel.technique.tactic").status_code == 200
    assert client.get("/api/v1/knowledge/version/T1078").json()["items"]
    assert client.post("/api/v1/knowledge/search", json={"query": "account takeover"}).json()["total"] >= 1
    assert client.get("/api/v1/knowledge/statistics").json()["item_count"] >= 8
    assert client.post("/api/v1/knowledge/T1078", json={}).status_code == 405
    assert client.get("/api/v1/knowledge/does-not-exist").status_code == 404
