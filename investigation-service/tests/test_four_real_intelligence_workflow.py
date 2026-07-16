from __future__ import annotations

import httpx

from app.agent.graph import GraphBuilder
from app.agent.state import InvestigationState, WorkflowStatus
from app.agent.tool_router import ToolRouter
from app.agent.tools.evidence_tool import EvidenceServiceHTTPClient, EvidenceToolAdapter
from app.agent.tools.graph_tool import GraphServiceHTTPClient, GraphToolAdapter
from app.agent.tools.knowledge_tool import KnowledgeServiceHTTPClient, KnowledgeToolAdapter
from app.agent.tools.threat_tool import ThreatServiceHTTPClient, ThreatToolAdapter
from app.agent.tools.mock_tools import mock_tool_set


def test_agent_uses_four_real_deterministic_intelligence_adapters():
    def handler(request):
        path = request.url.path
        if path == "/api/v1/evidence/search":
            return httpx.Response(200, json={"items": [{"evidence_id": "evidence-001", "evidence_type": "authentication_event", "confidence": 0.9}], "total": 1}, request=request)
        if path == "/api/v1/threat/search":
            return httpx.Response(200, json={"items": [{"threat_id": "threat-001", "pattern_name": "Account Takeover", "confidence": 82, "missing_evidence": []}], "confidence_breakdown": {"knowledge": 0.82, "pattern": 0.82, "graph": 0.71, "history": 0.62, "policy": 0.76}}, request=request)
        if path == "/api/v1/knowledge/search":
            return httpx.Response(200, json={"items": [{"id": "pattern.account_takeover", "name": "Account Takeover", "description": "Suspicious account access", "category": "generic"}], "total": 1}, request=request)
        if path == "/api/v1/graph/expand":
            return httpx.Response(200, json={"start_node_id": "evidence-001", "nodes": [{"id": "evidence-001", "entity_type": "evidence", "name": "Authentication evidence"}], "relationships": [], "paths": [], "depth": 1, "truncated": False}, request=request)
        raise AssertionError(f"unexpected service endpoint: {path}")

    def client(client_type, base_url, **kwargs):
        return client_type(base_url, client=httpx.Client(base_url=base_url, transport=httpx.MockTransport(handler)), **kwargs)

    tools = mock_tool_set()
    tools.update({
        "evidence": EvidenceToolAdapter(client(EvidenceServiceHTTPClient, "http://evidence-service")),
        "threat": ThreatToolAdapter(client(ThreatServiceHTTPClient, "http://threat-service")),
        "knowledge": KnowledgeToolAdapter(client(KnowledgeServiceHTTPClient, "http://knowledge-service")),
        "graph": GraphToolAdapter(client(GraphServiceHTTPClient, "http://graph-service")),
    })
    state = InvestigationState.new("investigation-four-source", "tenant-1")
    result = GraphBuilder(ToolRouter(tools)).build().invoke({"state": state.model_dump(mode="json")}, config={"configurable": {"thread_id": state.investigation_id}})
    completed = InvestigationState.model_validate(result["state"])

    assert completed.workflow_status is WorkflowStatus.COMPLETED
    assert completed.evidence[0]["evidence_id"] == "evidence-001"
    assert completed.graph_results["start_node_id"] == "evidence-001"
    assert completed.knowledge["items"][0]["id"] == "pattern.account_takeover"
