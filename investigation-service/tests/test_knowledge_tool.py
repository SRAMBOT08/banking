from __future__ import annotations

from threading import Event
import httpx

from app.agent.state import InvestigationState, WorkflowStatus
from app.agent.tools.knowledge_tool import KnowledgeServiceHTTPClient, KnowledgeToolAdapter


class FakeKnowledgeClient:
    def __init__(self, payload=None):
        self.payload = payload or {"items": [], "total": 0}
        self.calls = []

    def search(self, path, request=None, *, cancel_event=None, **kwargs):
        self.calls.append(("search", path, request, cancel_event))
        return self.payload

    def get(self, path, *, params=None, cancel_event=None, **kwargs):
        self.calls.append(("get", path, params, cancel_event))
        return self.payload


def test_knowledge_adapter_translates_search_without_mutating_state():
    client = FakeKnowledgeClient({"items": [{"id": "T1078"}], "total": 1})
    adapter = KnowledgeToolAdapter(client)
    state = InvestigationState.new("investigation-knowledge", "tenant-1")
    event = Event()

    result = adapter.execute(state, {"query": "valid accounts", "cancel_event": event})

    assert result["items"][0]["id"] == "T1078"
    assert client.calls[0][1] == "/api/v1/knowledge/search"
    assert client.calls[0][2]["investigation_id"] == "investigation-knowledge"
    assert client.calls[0][3] is event
    assert state.workflow_status is WorkflowStatus.NEW


def test_knowledge_adapter_routes_typed_queries():
    client = FakeKnowledgeClient({"id": "T1078"})
    adapter = KnowledgeToolAdapter(client)
    state = InvestigationState.new("i", "t")
    adapter.execute(state, {"operation": "technique", "id": "T1078"})
    adapter.execute(state, {"operation": "relationships", "id": "T1078"})
    assert client.calls[0][1].endswith("/mitre/technique/T1078")
    assert client.calls[1][1].endswith("/relationship/item/T1078")


def test_knowledge_adapter_preserves_hypothesis_list_contract():
    client = FakeKnowledgeClient({"items": [{"id": "pattern.account_takeover"}], "total": 1})
    adapter = KnowledgeToolAdapter(client)
    result = adapter.execute(InvestigationState.new("i", "t"), {"patterns": [{"id": "pattern.account_takeover"}]})
    assert result == [{"id": "pattern.account_takeover"}]


def test_knowledge_http_client_uses_sdk_transport():
    requests = []

    def handler(request):
        requests.append(request)
        return httpx.Response(200, json={"items": [], "total": 0}, request=request)

    http_client = httpx.Client(base_url="http://knowledge-service", transport=httpx.MockTransport(handler))
    client = KnowledgeServiceHTTPClient("http://knowledge-service", client=http_client)
    payload = client.search("/api/v1/knowledge/search", {"query": "mitre"})
    assert payload["total"] == 0
    assert requests[0].url.path == "/api/v1/knowledge/search"
