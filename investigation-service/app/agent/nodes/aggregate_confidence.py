from __future__ import annotations
from typing import Any
from ..state import InvestigationState, WorkflowStatus
from ..tool_router import ToolRouter
from ..confidence_manager import ConfidenceManager
from .common import run_node

def aggregate_confidence(state: InvestigationState, router: ToolRouter, params: dict[str, Any] | None = None) -> InvestigationState:
    def apply(current: InvestigationState, result: Any) -> None:
        scores = {
            item["source"]: item["score"]
            for item in current.intelligence_context.get("confidence_sources", [])
            if item.get("score") is not None
        }
        current.confidence_breakdown = ConfidenceManager().breakdown(scores)
        current.final_confidence = current.confidence_breakdown.get("final", 0.0)
    return run_node(state, router, "aggregate_confidence", WorkflowStatus.REPORT_GENERATION, None, {}, apply)
