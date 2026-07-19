from __future__ import annotations
from datetime import datetime, timezone
from typing import Optional
from app.models.investigation import Investigation, InvestigationPriority, InvestigationState
from app.engine.state_machine import can_transition


class InvestigationPolicy:
    """Operational policy boundary; orchestration code does not own policy rules."""
    def __init__(self, max_lifetime_seconds: int = 86400, escalation_confidence: int = 85, auto_close_after_seconds: int = 604800):
        self.max_lifetime_seconds = max_lifetime_seconds
        self.escalation_confidence = escalation_confidence
        self.auto_close_after_seconds = auto_close_after_seconds

    def validate_transition(self, current: InvestigationState, target: InvestigationState) -> bool:
        return can_transition(current, target)

    def should_escalate(self, investigation: Investigation) -> bool:
        return investigation.confidence.score >= self.escalation_confidence or investigation.priority == InvestigationPriority.CRITICAL

    def should_auto_close(self, investigation: Investigation, now: Optional[datetime] = None) -> bool:
        if investigation.state not in {InvestigationState.DECIDED, InvestigationState.ESCALATED, InvestigationState.APPROVED}:
            return False
        now = now or datetime.now(timezone.utc)
        created = datetime.fromisoformat(investigation.metadata.created_at.replace("Z", "+00:00"))
        return (now - created).total_seconds() >= self.auto_close_after_seconds

    def lifetime_exceeded(self, investigation: Investigation, now: Optional[datetime] = None) -> bool:
        now = now or datetime.now(timezone.utc)
        created = datetime.fromisoformat(investigation.metadata.created_at.replace("Z", "+00:00"))
        return (now - created).total_seconds() >= self.max_lifetime_seconds
