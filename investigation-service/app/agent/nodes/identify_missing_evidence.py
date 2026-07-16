from __future__ import annotations
from typing import Any
from ..state import InvestigationState, WorkflowStatus
from ..tool_router import ToolRouter
from .common import run_node

def identify_missing_evidence(state: InvestigationState, router: ToolRouter, params: dict[str, Any] | None = None) -> InvestigationState:
    def apply(current: InvestigationState, result: Any) -> None:
        current.missing_evidence = [{"source": item} for item in current.intelligence_context.get("missing_information", [])]
        current.tool_outputs["missing_evidence"] = current.missing_evidence
    return run_node(state, router, "identify_missing_evidence", WorkflowStatus.PATTERN_MATCHING, None, {}, apply)
