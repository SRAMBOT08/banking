from __future__ import annotations
from typing import Iterable, Optional
from app.models.investigation import Hypothesis, Investigation, InvestigationEvidence


def find_duplicate_hypothesis(investigation: Investigation, hypothesis: Hypothesis) -> Optional[Hypothesis]:
    return next((item for item in investigation.hypotheses
                 if item.pattern_name == hypothesis.pattern_name
                 and item.pattern_version == hypothesis.pattern_version), None)


def evidence_key(evidence: InvestigationEvidence) -> str:
    return evidence.evidence_id


def merge_hypothesis(existing: Hypothesis, incoming: Hypothesis) -> Hypothesis:
    existing.confidence = max(existing.confidence, incoming.confidence)
    existing.candidate_ids = sorted(set(existing.candidate_ids + incoming.candidate_ids))
    existing.matched_indicators = sorted(set(existing.matched_indicators + incoming.matched_indicators))
    existing.missing_indicators = sorted(set(existing.missing_indicators + incoming.missing_indicators))
    return existing
