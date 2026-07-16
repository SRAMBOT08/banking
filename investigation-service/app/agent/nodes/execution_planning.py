from __future__ import annotations
from typing import Any
from ..state import InvestigationState, WorkflowStatus
from ..tool_router import ToolRouter
from .common import run_node

def execution_planning(state: InvestigationState, router: ToolRouter, params: dict[str, Any] | None = None) -> InvestigationState:
    def apply(current: InvestigationState, result: Any) -> None:
        current.execution_plan = result if isinstance(result, dict) else {}
        current.tool_outputs["execution_plan"] = result
    updated = run_node(state, router, "execution_planning", WorkflowStatus.COMPLETED, "execution", params or {}, apply)
    return updated
