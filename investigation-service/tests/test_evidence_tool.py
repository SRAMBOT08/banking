from __future__ import annotations

from threading import Event

import httpx
import pytest

from app.agent.state import InvestigationState
from app.agent.graph import GraphBuilder
from app.agent.tool_router import ToolRouter
from app.agent.tools.evidence_tool import EvidenceOperation, EvidenceServiceHTTPClient, EvidenceToolAdapter, EvidenceToolError
from app.agent.tools.mock_tools import mock_tool_set


class FakeEvidenceClient:
    def __init__(self, payload=None, error=None):
        self.payload = payload or {}
        self.error = error
        self.calls = []

    def execute(self, operation, request, cancel_event=None):
        self.calls.append((operation, request, cancel_event))
        if self.error:
            raise self.error
        return self.payload


def test_evidence_adapter_translates_request_and_typed_response():
    client = FakeEvidenceClient(
        {
            "evidence": [{"evidence_id": "ev-1", "evidence_type": "login", "confidence": 0.9, "source": "events"}],
            "entities": [{"entity_type": "user", "canonical_id": "user-1", "attributes": {"id": "u-1"}}],
            "relationships": [{"source_id": "user-1", "target_id": "ip-1", "relationship_type": "used"}],
            "metadata": {"total": 1, "by_type": {"login": 1}, "source_count": 1, "service_version": "1.0"},
        }
    )
    adapter = EvidenceToolAdapter(client)
    state = InvestigationState.new("investigation-1", "tenant-1")
    cancel_event = Event()

    result = adapter.execute(state, {"operation": "retrieve", "entity_id": "user-1", "cancel_event": cancel_event})

    operation, request, received_event = client.calls[0]
    assert operation is EvidenceOperation.RETRIEVE
    assert received_event is cancel_event
    assert request["investigation_id"] == "investigation-1"
    assert request["tenant_id"] == "tenant-1"
    assert request["parameters"] == {"entity_id": "user-1"}
    assert result["evidence"][0]["evidence_id"] == "ev-1"
    assert result["entities"][0]["canonical_id"] == "user-1"
    assert result["relationships"][0]["relationship_type"] == "used"
    assert state.evidence == []


def test_evidence_adapter_supports_all_service_operations():
    client = FakeEvidenceClient()
    adapter = EvidenceToolAdapter(client)
    state = InvestigationState.new("investigation-2", "tenant-1")

    for operation in EvidenceOperation:
        adapter.execute(state, {"operation": operation.value})

    assert [call[0] for call in client.calls] == list(EvidenceOperation)


def test_http_client_uses_injected_endpoint_and_json_transport():
    requests = []

    def handler(request):
        requests.append(request)
        return httpx.Response(200, json={"evidence": [], "metadata": {"total": 0}}, request=request)

    http_client = httpx.Client(base_url="http://evidence-service", transport=httpx.MockTransport(handler))
    client = EvidenceServiceHTTPClient("http://evidence-service", client=http_client)
    payload = client.execute(EvidenceOperation.RETRIEVE, {"investigation_id": "i-1"})

    assert payload["metadata"]["total"] == 0
    assert requests[0].url.path == "/api/v1/evidence/search"
    assert requests[0].read().decode() == '{"investigation_id":"i-1"}'


def test_evidence_adapter_rejects_invalid_service_payload():
    client = FakeEvidenceClient({"evidence": [{"confidence": "not-a-number"}]})
    adapter = EvidenceToolAdapter(client)
    state = InvestigationState.new("investigation-3", "tenant-1")

    with pytest.raises(Exception):
        adapter.execute(state, {})


def test_evidence_adapter_preserves_client_failures():
    client = FakeEvidenceClient(error=EvidenceToolError("service unavailable"))
    adapter = EvidenceToolAdapter(client)
    state = InvestigationState.new("investigation-4", "tenant-1")

    with pytest.raises(EvidenceToolError, match="service unavailable"):
        adapter.execute(state, {})


def test_agent_workflow_runs_with_real_evidence_and_mock_remaining_tools():
    client = FakeEvidenceClient({
        "evidence": [{"evidence_id": "ev-real-1", "evidence_type": "authentication_event", "confidence": 0.95, "source": "evidence-service"}],
        "metadata": {"total": 1, "by_type": {"authentication_event": 1}, "source_count": 1},
    })
    tools = mock_tool_set()
    tools["evidence"] = EvidenceToolAdapter(client)
    graph = GraphBuilder(ToolRouter(tools)).build()
    state = InvestigationState.new("investigation-real-evidence", "tenant-1")

    result = graph.invoke({"state": state.model_dump(mode="json")}, config={"configurable": {"thread_id": state.investigation_id}})
    completed = InvestigationState.model_validate(result["state"])

    assert completed.workflow_status.value == "COMPLETED"
    assert completed.evidence[0]["evidence_id"] == "ev-real-1"
    assert client.calls[0][0] is EvidenceOperation.COLLECT
