from __future__ import annotations
from app.models.investigation import InvestigationState

TRANSITIONS = {
    InvestigationState.NEW: {InvestigationState.OPEN},
    InvestigationState.OPEN: {InvestigationState.COLLECTING_EVIDENCE, InvestigationState.CORRELATING, InvestigationState.CLOSED},
    InvestigationState.COLLECTING_EVIDENCE: {InvestigationState.CORRELATING, InvestigationState.WAITING_FOR_EVIDENCE},
    InvestigationState.CORRELATING: {InvestigationState.ANALYZING, InvestigationState.WAITING_FOR_EVIDENCE},
    InvestigationState.ANALYZING: {InvestigationState.READY_FOR_AI, InvestigationState.ESCALATED, InvestigationState.WAITING_FOR_EVIDENCE},
    InvestigationState.WAITING_FOR_EVIDENCE: {InvestigationState.COLLECTING_EVIDENCE, InvestigationState.READY_FOR_AI},
    InvestigationState.READY_FOR_AI: {InvestigationState.ESCALATED, InvestigationState.RESOLVED},
    InvestigationState.ESCALATED: {InvestigationState.RESOLVED, InvestigationState.CLOSED},
    InvestigationState.RESOLVED: {InvestigationState.CLOSED, InvestigationState.OPEN},
    InvestigationState.CLOSED: {InvestigationState.OPEN},
}


def can_transition(current: InvestigationState, target: InvestigationState) -> bool:
    return target in TRANSITIONS.get(current, set())


def transition(current: InvestigationState, target: InvestigationState) -> InvestigationState:
    if not can_transition(current, target):
        raise ValueError(f"invalid investigation transition: {current.value}->{target.value}")
    return target
