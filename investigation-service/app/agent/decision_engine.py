from __future__ import annotations

from enum import Enum
from typing import Any, Dict

from .state import InvestigationState, WorkflowStatus


class DecisionAction(str, Enum):
    CONTINUE = "continue"
    COLLECT_ADDITIONAL_EVIDENCE = "collect_additional_evidence"
    REQUIRE_HUMAN_APPROVAL = "require_human_approval"
    ESCALATE = "escalate"
    EXECUTION_ALLOWED = "execution_allowed"
    CLOSE = "close"


class DecisionEngine:
    """Deterministic policy boundary; it never calls services or models."""

    def __init__(self, approval_threshold: float = 0.8, escalation_threshold: float = 0.95):
        self.approval_threshold = approval_threshold
        self.escalation_threshold = escalation_threshold

    def decide(self, state: InvestigationState) -> Dict[str, Any]:
        confidence = state.final_confidence or 0.0
        if state.missing_evidence:
            action = DecisionAction.COLLECT_ADDITIONAL_EVIDENCE
        elif state.metadata.get("escalation_required") or confidence >= self.escalation_threshold:
            action = DecisionAction.ESCALATE
        elif state.metadata.get("human_approval_required") or confidence >= self.approval_threshold:
            action = DecisionAction.REQUIRE_HUMAN_APPROVAL
        elif state.metadata.get("close_investigation"):
            action = DecisionAction.CLOSE
        else:
            action = DecisionAction.EXECUTION_ALLOWED
        return {"action": action.value, "confidence": confidence, "hypothesis_count": len(state.hypotheses), "reason": self._reason(action, confidence)}

    @staticmethod
    def _reason(action: DecisionAction, confidence: float) -> str:
        return {DecisionAction.COLLECT_ADDITIONAL_EVIDENCE: "required evidence remains", DecisionAction.REQUIRE_HUMAN_APPROVAL: "policy requires human approval", DecisionAction.ESCALATE: "confidence or policy requires escalation", DecisionAction.CLOSE: "investigation closure requested", DecisionAction.EXECUTION_ALLOWED: "deterministic policy permits continuation", DecisionAction.CONTINUE: "workflow may continue"}[action]

    @staticmethod
    def route(decision: Dict[str, Any]) -> str:
        action = decision.get("action")
        if action == DecisionAction.REQUIRE_HUMAN_APPROVAL.value:
            return "approval"
        if action == DecisionAction.COLLECT_ADDITIONAL_EVIDENCE.value:
            return "more_evidence"
        if action in {DecisionAction.CLOSE.value, DecisionAction.ESCALATE.value}:
            return "approval"
        return "continue"
