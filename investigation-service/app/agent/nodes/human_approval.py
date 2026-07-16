from __future__ import annotations
from typing import Any
from ..state import InvestigationState, WorkflowStatus
from ..tool_router import ToolRouter
from .common import run_node

def human_approval(state: InvestigationState, router: ToolRouter, params: dict[str, Any] | None = None) -> InvestigationState:
    def apply(current: InvestigationState, result: Any) -> None:
        current.metadata["approval"] = result if result is not None else {"status": "pending"}
    return run_node(state, router, "human_approval", WorkflowStatus.REPORT_GENERATION, "memory", params or {"approval_request": True}, apply)
