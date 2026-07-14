from __future__ import annotations
from app.models.investigation import Investigation, InvestigationPriority


def assign_priority(investigation: Investigation) -> InvestigationPriority:
    score = investigation.confidence.score
    financial_impact = sum(int(item.properties.get("financial_impact", 0) or 0) for item in investigation.evidence)
    if score >= 85 or financial_impact >= 100000:
        return InvestigationPriority.CRITICAL
    if score >= 70 or financial_impact >= 10000:
        return InvestigationPriority.HIGH
    if score >= 40:
        return InvestigationPriority.MEDIUM
    return InvestigationPriority.LOW
