from __future__ import annotations
from typing import Any
from ..state import InvestigationState, WorkflowStatus
from ..tool_router import ToolRouter
from ..hypothesis_manager import HypothesisManager
from .common import run_node

def generate_hypotheses(state: InvestigationState, router: ToolRouter, params: dict[str, Any] | None = None) -> InvestigationState:
    def apply(current: InvestigationState, result: Any) -> None:
        patterns = current.matched_patterns
        current.hypotheses = HypothesisManager().generate(patterns)
        current.tool_outputs["hypotheses"] = patterns
    return run_node(state, router, "generate_hypotheses", WorkflowStatus.CONFIDENCE_AGGREGATION, None, {}, apply)
