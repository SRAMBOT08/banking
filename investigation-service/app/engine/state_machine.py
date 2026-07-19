from __future__ import annotations
from app.models.investigation import InvestigationState

TRANSITIONS = {
    InvestigationState.NEW: {InvestigationState.OPEN},
    InvestigationState.OPEN: {InvestigationState.CORRELATING, InvestigationState.CLOSED},
    InvestigationState.CORRELATING: {InvestigationState.ANALYZING, InvestigationState.WAITING_FOR_EVIDENCE, InvestigationState.CLOSED},
    InvestigationState.ANALYZING: {InvestigationState.READY_FOR_DECISION, InvestigationState.ESCALATED, InvestigationState.WAITING_FOR_EVIDENCE, InvestigationState.CLOSED},
    InvestigationState.WAITING_FOR_EVIDENCE: {InvestigationState.CORRELATING, InvestigationState.READY_FOR_DECISION, InvestigationState.CLOSED},
    InvestigationState.READY_FOR_DECISION: {InvestigationState.DECIDED, InvestigationState.ESCALATED, InvestigationState.CLOSED},
    InvestigationState.ESCALATED: {InvestigationState.DECIDED, InvestigationState.CLOSED},
    InvestigationState.DECIDED: {InvestigationState.APPROVED, InvestigationState.REJECTED, InvestigationState.CLOSED},
    InvestigationState.APPROVED: {InvestigationState.CLOSED, InvestigationState.ARCHIVED},
    InvestigationState.REJECTED: {InvestigationState.WAITING_FOR_EVIDENCE, InvestigationState.CLOSED},
    InvestigationState.CLOSED: {InvestigationState.OPEN, InvestigationState.ARCHIVED},
    InvestigationState.ARCHIVED: set(),
}


def can_transition(current: InvestigationState, target: InvestigationState) -> bool:
    return target in TRANSITIONS.get(current, set())


def transition(current: InvestigationState, target: InvestigationState) -> InvestigationState:
    if not can_transition(current, target):
        raise ValueError(f"invalid investigation transition: {current.value}->{target.value}")
    return target
