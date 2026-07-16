from __future__ import annotations

from threading import Event
import httpx

from app.agent.state import InvestigationState, WorkflowStatus
from app.agent.tools.memory_tool import InvestigationMemoryHTTPClient, InvestigationMemoryToolAdapter


class FakeMemoryClient:
    def __init__(self, payload=None):
        self.payload = payload or {"items": [], "total": 0}
        self.calls = []

    def get(self, path, *, params=None, cancel_event=None, correlation_id=None, **kwargs):
        self.calls.append(("GET", path, params, cancel_event, correlation_id))
        return self.payload

    def post(self, path, request=None, *, cancel_event=None, correlation_id=None, **kwargs):
        self.calls.append(("POST", path, request, cancel_event, correlation_id))
        return self.payload


def test_memory_adapter_search_translates_current_intelligence_without_mutation():
    client = FakeMemoryClient({"items": [{"investigation_id": "investigation-history-001"}], "total": 1})
    adapter = InvestigationMemoryToolAdapter(client)
    state = InvestigationState.new("investigation-current", "tenant-1")
    state.evidence = [{"evidence_type": "authentication_event"}]
    state.matched_patterns = [{"pattern_name": "Account Takeover"}]
    state.knowledge = {"items": [{"id": "pattern.account_takeover"}]}
    state.graph_results = {"nodes": [{"id": "device-001"}]}
    before = state.model_dump(mode="json")
    event = Event()
    result = adapter.execute(state, {"cancel_event": event})
    assert result["items"][0]["investigation_id"] == "investigation-history-001"
    assert client.calls[0][0] == "POST"
    assert client.calls[0][1] == "/api/v1/memory/search"
    assert client.calls[0][2]["evidence_types"] == ["authentication_event"]
    assert client.calls[0][2]["threat_patterns"] == ["Account Takeover"]
    assert client.calls[0][3] is event
    assert client.calls[0][4] == "investigation-current"
    assert state.model_dump(mode="json") == before


def test_memory_adapter_routes_explicit_historical_queries():
    client = FakeMemoryClient({"outcome_type": "account_protected", "success": True})
    adapter = InvestigationMemoryToolAdapter(client)
    state = InvestigationState.new("i", "t")
    adapter.execute(state, {"operation": "outcome", "investigation_id": "investigation-history-001"})
    adapter.execute(state, {"operation": "timeline", "entity_id": "account-001"})
    assert client.calls[0][1].endswith("/outcome/investigation-history-001")
    assert client.calls[1][1].endswith("/timeline/account-001")


def test_memory_http_client_uses_shared_sdk_transport():
    requests = []
    def handler(request):
        requests.append(request)
        return httpx.Response(200, json={"investigation_count": 3}, request=request)
    http_client = httpx.Client(base_url="http://memory-service", transport=httpx.MockTransport(handler))
    client = InvestigationMemoryHTTPClient("http://memory-service", client=http_client)
    assert client.get("/api/v1/memory/statistics")["investigation_count"] == 3
    assert requests[0].url.path == "/api/v1/memory/statistics"
