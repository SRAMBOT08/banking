from __future__ import annotations

from threading import Event
import httpx

from app.agent.state import InvestigationState, WorkflowStatus
from app.agent.tools.graph_tool import GraphServiceHTTPClient, GraphToolAdapter


class FakeGraphClient:
    def __init__(self):
        self.calls = []

    def get(self, path, *, params=None, cancel_event=None, correlation_id=None, **kwargs):
        self.calls.append(("GET", path, params, cancel_event, correlation_id))
        return {"nodes": [], "relationships": [], "operation": "get"}

    def post(self, path, request=None, *, cancel_event=None, correlation_id=None, **kwargs):
        self.calls.append(("POST", path, request, cancel_event, correlation_id))
        return {"nodes": [], "relationships": [], "operation": "post"}


def test_graph_adapter_translates_queries_without_state_mutation():
    client = FakeGraphClient()
    adapter = GraphToolAdapter(client)
    state = InvestigationState.new("investigation-graph", "tenant-1")
    before = state.model_dump(mode="json")
    event = Event()
    result = adapter.execute(state, {"operation": "neighborhood", "node_id": "account-001", "depth": 2, "cancel_event": event})
    assert result["operation"] == "get"
    assert client.calls[0][1].endswith("/node/account-001/neighbors")
    assert client.calls[0][2]["depth"] == 2
    assert client.calls[0][3] is event
    assert client.calls[0][4] == "investigation-graph"
    assert state.model_dump(mode="json") == before


def test_graph_http_client_uses_shared_sdk_transport():
    requests = []
    def handler(request):
        requests.append(request)
        return httpx.Response(200, json={"node_count": 15}, request=request)
    http_client = httpx.Client(base_url="http://graph-service", transport=httpx.MockTransport(handler))
    client = GraphServiceHTTPClient("http://graph-service", client=http_client)
    assert client.get("/api/v1/graph/statistics")["node_count"] == 15
    assert requests[0].url.path == "/api/v1/graph/statistics"
