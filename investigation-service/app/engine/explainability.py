from __future__ import annotations
from app.models.investigation import Investigation


def explain(investigation: Investigation):
    reasons = [f"Investigation contains {len(investigation.hypotheses)} hypothesis(es).",
               f"Confidence is {investigation.confidence.score}.",
               f"Priority is {investigation.priority.value}."]
    if investigation.missing_evidence:
        reasons.append("Missing evidence: " + ", ".join(item.evidence_type for item in investigation.missing_evidence) + ".")
    else:
        reasons.append("No required evidence is currently missing.")
    return reasons
