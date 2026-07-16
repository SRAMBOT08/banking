from __future__ import annotations

from threading import Event

import httpx

from app.agent.graph import GraphBuilder
from app.agent.state import InvestigationState, WorkflowStatus
from app.agent.tool_router import ToolRouter
from app.agent.tools.mock_tools import mock_tool_set
from app.agent.tools.threat_tool import ThreatServiceHTTPClient, ThreatToolAdapter


class FakeThreatClient:
    def __init__(self, payload):
        self.payload = payload
        self.calls = []

    def search(self, request, cancel_event=None):
        self.calls.append((request, cancel_event))
        return self.payload

    def get(self, path, params=None, cancel_event=None):
        self.calls.append((path, params, cancel_event))
        return self.payload


def candidate_payload():
    return {
        "items": [{
            "threat_id": "threat-1",
            "pattern_name": "account_takeover",
            "pattern_version": "1",
            "confidence": 60,
            "investigation_id": "investigation-threat",
            "explanation": {"reason": "stored match"},
            "evidence_refs": [{"id": "ev-1"}],
            "missing_evidence": [],
        }]
    }


def test_threat_adapter_maps_typed_query_results_without_state_mutation():
    client = FakeThreatClient(candidate_payload())
    adapter = ThreatToolAdapter(client)
    state = InvestigationState.new("investigation-threat", "tenant-1")
    cancel_event = Event()

    result = adapter.execute(state, [{"id": "ev-1"}])

    assert result[0]["threat_id"] == "threat-1"
    assert client.calls[0][1] is None
    assert state.workflow_status is WorkflowStatus.NEW

    missing = adapter.execute(state, {"missing_evidence_check": True, "cancel_event": cancel_event})
    assert missing == {"missing_evidence": []}
    assert client.calls[-1][1] is cancel_event


def test_threat_http_client_uses_query_search_endpoint():
    requests = []

    def handler(request):
        requests.append(request)
        return httpx.Response(200, json=candidate_payload(), request=request)

    client = ThreatServiceHTTPClient("http://threat-service", client=httpx.Client(base_url="http://threat-service", transport=httpx.MockTransport(handler)))
    payload = client.search({"investigation_id": "investigation-threat"})

    assert payload["items"][0]["threat_id"] == "threat-1"
    assert requests[0].url.path == "/api/v1/threat/search"


def test_agent_workflow_runs_with_real_threat_and_mock_remaining_tools():
    tools = mock_tool_set()
    tools["threat"] = ThreatToolAdapter(FakeThreatClient({**candidate_payload(), "confidence_breakdown": {"pattern": 0.6}}))
    graph = GraphBuilder(ToolRouter(tools)).build()
    state = InvestigationState.new("investigation-threat", "tenant-1")

    result = graph.invoke({"state": state.model_dump(mode="json")}, config={"configurable": {"thread_id": state.investigation_id}})
    completed = InvestigationState.model_validate(result["state"])

    assert completed.workflow_status is WorkflowStatus.COMPLETED
    assert completed.matched_patterns[0]["threat_id"] == "threat-1"
