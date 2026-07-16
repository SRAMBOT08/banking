from __future__ import annotations

from typing import Any

from ..decision_engine import DecisionEngine
from ..state import InvestigationState, WorkflowStatus
from ..tool_router import ToolRouter
from .common import run_node


def decision_engine(state: InvestigationState, router: ToolRouter, params: dict[str, Any] | None = None) -> InvestigationState:
    engine = (params or {}).get("engine") or DecisionEngine()

    def apply(current: InvestigationState, result: Any) -> None:
        decision = engine.decide(current)
        current.metadata["decision"] = decision
        current.tool_outputs["decision"] = decision
        current.add_history({"event": "decision", **decision})

    return run_node(state, router, "decision_engine", WorkflowStatus.DECISION_ENGINE, None, params or {}, apply)
