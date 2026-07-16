from __future__ import annotations

import httpx

from app.agent.graph import GraphBuilder
from app.agent.state import InvestigationState, WorkflowStatus
from app.agent.tool_router import ToolRouter
from app.agent.tools.evidence_tool import EvidenceToolAdapter
from app.agent.tools.knowledge_tool import KnowledgeServiceHTTPClient, KnowledgeToolAdapter
from app.agent.tools.mock_tools import mock_tool_set
from app.agent.tools.threat_tool import ThreatToolAdapter


def test_mixed_workflow_uses_real_evidence_threat_and_knowledge_adapters():
    def handler(request):
        if request.url.path == "/api/v1/knowledge/search":
            return httpx.Response(200, json={"items": [{"id": "T1078", "name": "Valid Accounts", "category": "mitre_technique", "description": "valid account"}], "total": 1}, request=request)
        raise AssertionError(f"unexpected knowledge endpoint: {request.url.path}")

    knowledge_client = KnowledgeServiceHTTPClient("http://knowledge-service", client=httpx.Client(base_url="http://knowledge-service", transport=httpx.MockTransport(handler)))
    tools = mock_tool_set()
    # Evidence and Threat remain the already-integrated deterministic fakes for this
    # focused workflow; the Knowledge adapter is the real SDK-backed integration.
    tools["knowledge"] = KnowledgeToolAdapter(knowledge_client)
    graph = GraphBuilder(ToolRouter(tools)).build()
    state = InvestigationState.new("investigation-knowledge", "tenant-1")

    result = graph.invoke({"state": state.model_dump(mode="json")}, config={"configurable": {"thread_id": state.investigation_id}})
    completed = InvestigationState.model_validate(result["state"])

    assert completed.workflow_status is WorkflowStatus.COMPLETED
    assert completed.knowledge["items"][0]["id"] == "T1078"
