from __future__ import annotations
from typing import Any
from ..state import InvestigationState, WorkflowStatus
from ..tool_router import ToolRouter
from .common import run_node

def build_investigation(state: InvestigationState, router: ToolRouter, params: dict[str, Any] | None = None) -> InvestigationState:
    def apply(current: InvestigationState, result: Any) -> None:
        current.recommendations = result.get("recommendations", []) if isinstance(result, dict) else []
        current.tool_outputs["investigation"] = result
    return run_node(state, router, "build_investigation", WorkflowStatus.REPORT_GENERATION, "memory", params or {}, apply)
