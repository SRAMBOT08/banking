from __future__ import annotations
from typing import Any
from ..state import InvestigationState, WorkflowStatus
from ..tool_router import ToolRouter
from .common import run_node

def graph_analysis(state: InvestigationState, router: ToolRouter, params: dict[str, Any] | None = None) -> InvestigationState:
    def apply(current: InvestigationState, result: Any) -> None:
        current.graph_results = current.intelligence_context.get("graph_context", {})
        current.tool_outputs["graph"] = current.graph_results
    return run_node(state, router, "graph_analysis", WorkflowStatus.HISTORY_ANALYSIS, None, {}, apply)
