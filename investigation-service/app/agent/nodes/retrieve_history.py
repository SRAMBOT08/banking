from __future__ import annotations
from typing import Any
from ..state import InvestigationState, WorkflowStatus
from ..tool_router import ToolRouter
from .common import run_node

def retrieve_history(state: InvestigationState, router: ToolRouter, params: dict[str, Any] | None = None) -> InvestigationState:
    def apply(current: InvestigationState, result: Any) -> None:
        history = current.intelligence_context.get("historical_context", {})
        current.tool_outputs["history"] = history
        current.metadata["historical_investigations"] = history.get("items", [])
    return run_node(state, router, "retrieve_history", WorkflowStatus.HYPOTHESIS_GENERATION, None, {}, apply)
