from __future__ import annotations
from typing import Any
from ..state import InvestigationState, WorkflowStatus
from ..tool_router import ToolRouter
from .common import run_node

def generate_ai_report(state: InvestigationState, router: ToolRouter, params: dict[str, Any] | None = None) -> InvestigationState:
    def apply(current: InvestigationState, result: Any) -> None:
        current.ai_summary = result if isinstance(result, str) else (result.get("summary", "") if isinstance(result, dict) else "")
        current.tool_outputs["ai_report"] = result
    return run_node(state, router, "generate_ai_report", WorkflowStatus.EXECUTION_PLANNING, "ai", params or {"investigation": state.model_dump() if hasattr(state, "model_dump") else state.dict()}, apply)
