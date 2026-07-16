from __future__ import annotations

import httpx

from app.agent.graph import GraphBuilder
from app.agent.state import InvestigationState, WorkflowStatus
from app.agent.tool_router import ToolRouter
from app.agent.tools.memory_tool import InvestigationMemoryHTTPClient, InvestigationMemoryToolAdapter
from app.agent.tools.mock_tools import mock_tool_set


def test_agent_uses_real_memory_adapter_with_unchanged_workflow():
    def handler(request):
        if request.url.path == "/api/v1/memory/search":
            return httpx.Response(200, json={"items": [{"investigation_id": "investigation-history-001", "title": "Account Takeover Investigation", "summary": "Historical case", "severity": "high", "case_status": "closed", "fraud_category": "account_takeover", "final_confidence": 0.88, "mitre_mapping": ["T1078"], "tags": ["historical"]}], "total": 1, "offset": 0, "limit": 100}, request=request)
        raise AssertionError(request.url.path)

    client = InvestigationMemoryHTTPClient("http://memory-service", client=httpx.Client(base_url="http://memory-service", transport=httpx.MockTransport(handler)))
    tools = mock_tool_set()
    tools["memory"] = InvestigationMemoryToolAdapter(client)
    state = InvestigationState.new("investigation-memory", "tenant-1")
    result = GraphBuilder(ToolRouter(tools)).build().invoke({"state": state.model_dump(mode="json")}, config={"configurable": {"thread_id": state.investigation_id}})
    completed = InvestigationState.model_validate(result["state"])
    assert completed.workflow_status is WorkflowStatus.COMPLETED
    assert completed.metadata["historical_investigations"]["items"][0]["investigation_id"] == "investigation-history-001"
