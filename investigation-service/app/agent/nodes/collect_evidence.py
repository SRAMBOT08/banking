from __future__ import annotations
from typing import Any, Dict
from ..state import InvestigationState, WorkflowStatus
from ..tool_router import ToolRouter
from .common import run_node


def collect_evidence(state: InvestigationState, router: ToolRouter, params: Dict[str, Any] | None = None) -> InvestigationState:
    def apply(current: InvestigationState, result: Any) -> None:
        if isinstance(result, InvestigationState):
            current.evidence = result.evidence
            current.tool_outputs["evidence"] = result.tool_outputs.get("evidence", result.evidence)
        elif isinstance(result, dict):
            current.evidence.extend(result.get("evidence", []))
            current.tool_outputs["evidence"] = result
        current.metadata["evidence_round"] = int(current.metadata.get("evidence_round", 0)) + 1
    return run_node(state, router, "collect_evidence", WorkflowStatus.KNOWLEDGE_RETRIEVAL, "evidence", params or {}, apply)
