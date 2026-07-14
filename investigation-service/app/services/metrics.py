from __future__ import annotations
from datetime import datetime, timezone
from typing import Iterable
from app.models.investigation import InvestigationState
from app.models.metrics import InvestigationMetrics


class InvestigationMetricsEngine:
    def snapshot(self, investigations: Iterable) -> InvestigationMetrics:
        items = list(investigations)
        now = datetime.now(timezone.utc)
        metrics = InvestigationMetrics()
        metrics.open_investigations = sum(item.state != InvestigationState.CLOSED for item in items)
        metrics.closed_investigations = sum(item.state == InvestigationState.CLOSED for item in items)
        metrics.evidence_count = sum(len(item.evidence) for item in items)
        metrics.average_confidence = round(sum(item.confidence.score for item in items) / len(items), 2) if items else 0
        durations = []
        for item in items:
            if item.state == InvestigationState.CLOSED:
                created = datetime.fromisoformat(item.metadata.created_at.replace("Z", "+00:00"))
                updated = datetime.fromisoformat(item.metadata.updated_at.replace("Z", "+00:00"))
                durations.append(max(0, (updated - created).total_seconds()))
        metrics.average_investigation_time_seconds = round(sum(durations) / len(durations), 2) if durations else 0
        for item in items:
            metrics.priority_distribution[item.priority.value] = metrics.priority_distribution.get(item.priority.value, 0) + 1
            metrics.state_distribution[item.state.value] = metrics.state_distribution.get(item.state.value, 0) + 1
            for hypothesis in item.hypotheses:
                metrics.pattern_distribution[hypothesis.pattern_name] = metrics.pattern_distribution.get(hypothesis.pattern_name, 0) + 1
                metrics.attack_type_distribution[hypothesis.pattern_name] = metrics.attack_type_distribution.get(hypothesis.pattern_name, 0) + 1
            for missing in item.missing_evidence:
                metrics.missing_evidence_frequency[missing.evidence_type] = metrics.missing_evidence_frequency.get(missing.evidence_type, 0) + 1
            for recommendation in item.investigation_plan:
                metrics.recommendation_frequency[recommendation.recommendation_id] = metrics.recommendation_frequency.get(recommendation.recommendation_id, 0) + 1
        return metrics
