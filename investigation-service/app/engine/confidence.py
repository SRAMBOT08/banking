from __future__ import annotations
from typing import List
from app.models.investigation import Investigation, InvestigationConfidence


def aggregate_confidence(investigation: Investigation) -> InvestigationConfidence:
    hypotheses = investigation.hypotheses
    pattern_score = round(sum(item.confidence for item in hypotheses) / len(hypotheses)) if hypotheses else 0
    evidence_score = investigation.evidence_summary.average_confidence
    correlation_score = min(100, 25 * max(0, len(investigation.related_entities)))
    required = sum(len(item.missing_indicators) for item in hypotheses)
    completeness_score = 100 if not hypotheses else max(0, round(100 * (1 - required / max(1, sum(len(item.matched_indicators) + len(item.missing_indicators) for item in hypotheses)))))
    historical_score = round(sum(item.score for item in investigation.confidence_history) / len(investigation.confidence_history)) if investigation.confidence_history else 0
    score = round(pattern_score * .5 + evidence_score * .2 + correlation_score * .1 + completeness_score * .15 + historical_score * .05)
    return InvestigationConfidence(score=min(100, score), pattern_score=pattern_score, evidence_score=evidence_score,
                                    correlation_score=correlation_score, completeness_score=completeness_score,
                                    historical_score=historical_score,
                                    explanation=[f"Pattern confidence is {pattern_score}.", f"Evidence completeness is {completeness_score}%."])
