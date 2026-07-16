from __future__ import annotations

from enum import Enum
from typing import Any, Dict, Iterable, List

from .state import InvestigationState, WorkflowStatus


class NextAction(str, Enum):
    COLLECT_MORE_EVIDENCE = "collect_more_evidence"
    CONTINUE = "continue"
    WAIT_FOR_APPROVAL = "wait_for_approval"
    COMPLETE = "complete"


class ReasoningEngine:
    """Deterministic coordinator over outputs from intelligence engines."""

    def __init__(self, minimum_evidence: int = 1, approval_threshold: float = 0.8):
        self.minimum_evidence = minimum_evidence
        self.approval_threshold = approval_threshold

    def needs_more_evidence(self, state: InvestigationState) -> bool:
        explicit = state.metadata.get("additional_evidence_required")
        if explicit is not None:
            return bool(explicit) and state.metadata.get("evidence_round", 0) < state.metadata.get("max_evidence_rounds", 1)
        return len(state.evidence) < self.minimum_evidence and state.metadata.get("evidence_round", 0) < state.metadata.get("max_evidence_rounds", 1)

    def evidence_complete(self, state: InvestigationState) -> bool:
        return not self.needs_more_evidence(state) and not state.missing_evidence

    def next_tool(self, state: InvestigationState) -> str:
        return {
            WorkflowStatus.COLLECTING_EVIDENCE: "evidence",
            WorkflowStatus.KNOWLEDGE_RETRIEVAL: "knowledge",
            WorkflowStatus.PATTERN_MATCHING: "threat",
            WorkflowStatus.GRAPH_ANALYSIS: "graph",
            WorkflowStatus.HISTORY_ANALYSIS: "memory",
            WorkflowStatus.REPORT_GENERATION: "ai",
            WorkflowStatus.EXECUTION_PLANNING: "execution",
        }.get(state.workflow_status, "")

    def requires_approval(self, state: InvestigationState) -> bool:
        return bool(state.metadata.get("human_approval_required", False)) or (state.final_confidence or 0.0) >= self.approval_threshold

    def select_hypothesis(self, hypotheses: Iterable[Dict[str, Any]]) -> Dict[str, Any] | None:
        candidates = [h for h in hypotheses if h.get("status", "active") == "active"]
        return max(candidates, key=lambda item: (float(item.get("confidence", 0.0)), int(item.get("priority", 0))), default=None)

    def next_action(self, state: InvestigationState) -> NextAction:
        if self.needs_more_evidence(state):
            return NextAction.COLLECT_MORE_EVIDENCE
        if state.workflow_status == WorkflowStatus.CONFIDENCE_AGGREGATION and self.requires_approval(state):
            return NextAction.WAIT_FOR_APPROVAL
        if state.workflow_status == WorkflowStatus.EXECUTION_PLANNING:
            return NextAction.COMPLETE
        return NextAction.CONTINUE

    def evaluate(self, state: InvestigationState) -> Dict[str, Any]:
        selected = self.select_hypothesis(state.hypotheses)
        return {"action": self.next_action(state).value, "next_tool": self.next_tool(state), "selected_hypothesis": selected, "evidence_complete": self.evidence_complete(state), "approval_required": self.requires_approval(state)}
