from __future__ import annotations

import httpx

from app.agent.graph import GraphBuilder
from app.agent.state import InvestigationState, WorkflowStatus
from app.agent.tool_router import ToolRouter
from app.agent.tools.graph_tool import GraphServiceHTTPClient, GraphToolAdapter
from app.agent.tools.mock_tools import mock_tool_set


def test_agent_workflow_consumes_real_graph_adapter_with_other_late_stage_tools_mocked():
    def handler(request):
        if request.url.path == "/api/v1/graph/expand":
            return httpx.Response(200, json={"start_node_id": "account-001", "nodes": [{"id": "account-001", "entity_type": "account", "name": "Account"}], "relationships": [], "paths": [], "depth": 1, "truncated": False}, request=request)
        raise AssertionError(request.url.path)

    client = GraphServiceHTTPClient("http://graph-service", client=httpx.Client(base_url="http://graph-service", transport=httpx.MockTransport(handler)))
    tools = mock_tool_set()
    tools["graph"] = GraphToolAdapter(client)
    state = InvestigationState.new("investigation-graph", "tenant-1")
    result = GraphBuilder(ToolRouter(tools)).build().invoke({"state": state.model_dump(mode="json")}, config={"configurable": {"thread_id": state.investigation_id}})
    completed = InvestigationState.model_validate(result["state"])
    assert completed.workflow_status is WorkflowStatus.COMPLETED
    assert completed.graph_results["start_node_id"] == "account-001"
