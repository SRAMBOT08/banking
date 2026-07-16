from __future__ import annotations
from typing import Any
from ..state import InvestigationState, WorkflowStatus
from ..tool_router import ToolRouter
from .common import run_node

def run_pattern_matching(state: InvestigationState, router: ToolRouter, params: dict[str, Any] | None = None) -> InvestigationState:
    def apply(current: InvestigationState, result: Any) -> None:
        context = current.intelligence_context
        current.matched_patterns = context.get("threat_context", {}).get("items", current.matched_patterns)
        current.tool_outputs["threat"] = context.get("threat_context", {})
    return run_node(state, router, "run_pattern_matching", WorkflowStatus.GRAPH_ANALYSIS, None, {}, apply)
