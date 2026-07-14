from __future__ import annotations
from app.models.investigation import Investigation, MissingEvidence, InvestigationPriority


def identify_missing_evidence(investigation: Investigation):
    missing = {}
    for hypothesis in investigation.hypotheses:
        for indicator in hypothesis.missing_indicators:
            missing.setdefault(indicator, MissingEvidence(evidence_type=indicator, reason=f"Required by {hypothesis.pattern_name}", priority=InvestigationPriority.HIGH))
    return sorted(missing.values(), key=lambda item: (item.priority.value, item.evidence_type))
