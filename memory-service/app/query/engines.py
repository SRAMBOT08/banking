from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
from typing import Iterable, Mapping

from .models import (
    CaseSimilarity, InvestigationRecord, InvestigationSearchRequest, InvestigationSimilarity,
    InvestigationStatistics, InvestigationTimeline, SimilarityRequest,
)


class DeterministicSimilarityEngine:
    """Pluggable similarity boundary with a deterministic feature scorer."""

    DIMENSIONS = ("evidence", "threat", "knowledge", "graph", "mitre", "fraud", "outcome", "decision", "resolution", "risk", "confidence")

    @staticmethod
    def _set(values: Iterable[str]) -> set[str]:
        return {str(value).casefold() for value in values if value}

    def score(self, source: SimilarityRequest, candidate: InvestigationRecord) -> CaseSimilarity:
        snapshot = candidate.snapshot
        features: list[str] = []
        breakdown: dict[str, float] = {}

        evidence = self._set(source.evidence_types)
        candidate_evidence = self._set(item.evidence_type for item in snapshot.evidence_references)
        if evidence:
            breakdown["evidence"] = len(evidence & candidate_evidence) / max(len(evidence | candidate_evidence), 1)
            if evidence & candidate_evidence: features.append("evidence_type")

        threats = self._set(source.threat_patterns)
        candidate_threats = self._set(item.pattern_name for item in snapshot.threat_references)
        if threats:
            breakdown["threat"] = len(threats & candidate_threats) / max(len(threats | candidate_threats), 1)
            if threats & candidate_threats: features.append("threat_pattern")

        knowledge = self._set(source.knowledge_references)
        candidate_knowledge = self._set(item.knowledge_id for item in snapshot.knowledge_references)
        if knowledge:
            breakdown["knowledge"] = len(knowledge & candidate_knowledge) / max(len(knowledge | candidate_knowledge), 1)
            if knowledge & candidate_knowledge: features.append("knowledge_reference")

        graph = self._set(source.graph_references)
        candidate_graph = self._set(item.community_id for item in snapshot.graph_references)
        if graph:
            breakdown["graph"] = len(graph & candidate_graph) / max(len(graph | candidate_graph), 1)
            if graph & candidate_graph: features.append("graph_community")

        mitre = self._set(source.mitre_mapping)
        candidate_mitre = self._set(snapshot.summary.mitre_mapping)
        if mitre:
            breakdown["mitre"] = len(mitre & candidate_mitre) / max(len(mitre | candidate_mitre), 1)
            if mitre & candidate_mitre: features.append("mitre_mapping")

        breakdown["fraud"] = float(bool(source.fraud_category and source.fraud_category == snapshot.summary.fraud_category))
        if breakdown["fraud"]: features.append("fraud_category")
        breakdown["outcome"] = float(bool(source.outcome_type and source.outcome_type == snapshot.outcome.outcome_type))
        if breakdown["outcome"]: features.append("outcome")
        breakdown["decision"] = float(bool(source.decision and snapshot.decision and source.decision.casefold() == snapshot.decision.decision.casefold()))
        if breakdown["decision"]: features.append("decision")
        breakdown["resolution"] = float(bool(source.resolution and snapshot.resolution and source.resolution.casefold() == snapshot.resolution.casefold()))
        if breakdown["resolution"]: features.append("resolution")
        if source.risk_score is not None:
            candidate_risk = float(snapshot.similarity_features.get("risk_score", snapshot.summary.final_confidence * 100))
            breakdown["risk"] = max(0.0, 1.0 - abs(source.risk_score - candidate_risk) / 100.0)
        if source.confidence is not None:
            breakdown["confidence"] = max(0.0, 1.0 - abs(source.confidence - snapshot.confidence.overall))

        if not breakdown:
            breakdown = {"historical": 0.0}
        score = sum(breakdown.values()) / len(breakdown)
        return CaseSimilarity(investigation_id=snapshot.summary.investigation_id, score=round(score, 6), explanation=f"Matched deterministic features: {', '.join(features) if features else 'none'}", matching_features=features)

    def compare(self, source: SimilarityRequest, records: Iterable[InvestigationRecord]) -> InvestigationSimilarity:
        matches = sorted((self.score(source, record) for record in records if record.snapshot.summary.investigation_id != source.investigation_id), key=lambda item: item.score, reverse=True)
        matches = matches[:source.limit]
        feature_breakdown: dict[str, float] = {}
        for match in matches:
            for feature in match.matching_features:
                feature_breakdown[feature] = feature_breakdown.get(feature, 0.0) + match.score
        return InvestigationSimilarity(source_investigation_id=source.investigation_id or "query", matching_investigation_ids=[item.investigation_id for item in matches], overall_score=round(matches[0].score if matches else 0.0, 6), feature_breakdown={key: round(value / len(matches), 6) for key, value in feature_breakdown.items()} if matches else {}, matching_features={item.investigation_id: item.matching_features for item in matches}, explanations=[item.explanation for item in matches])


class InvestigationTimelineEngine:
    def investigation(self, record: InvestigationRecord) -> InvestigationTimeline:
        return record.snapshot.timeline

    def entity(self, records: Iterable[InvestigationRecord], entity_id: str, timeline_type: str = "entity") -> InvestigationTimeline:
        events = []
        for record in records:
            for event in record.snapshot.timeline.events:
                if event.entity_id == entity_id or entity_id in record.snapshot.similarity_features.get("entity_ids", []):
                    events.append(event)
        source_id = events[0].event_id if events else entity_id
        return InvestigationTimeline(investigation_id=source_id, entity_id=entity_id, timeline_type=timeline_type, events=sorted(events, key=lambda event: event.timestamp))


class InvestigationStatisticsEngine:
    def calculate(self, records: Iterable[InvestigationRecord]) -> InvestigationStatistics:
        records = list(records)
        outcomes = Counter(record.snapshot.outcome.outcome_type.value for record in records)
        attacks = Counter(record.snapshot.summary.fraud_category or "unknown" for record in records)
        analysts = Counter(record.snapshot.metadata.analyst_id or "unknown" for record in records)
        trends = Counter(record.snapshot.metadata.completed_at.strftime("%Y-%m") for record in records)
        count = len(records)
        successful = sum(record.snapshot.outcome.success for record in records)
        false_positive = sum(record.snapshot.outcome.outcome_type.value == "false_positive" for record in records)
        return InvestigationStatistics(investigation_count=count, attack_frequency=dict(attacks), investigation_frequency=dict(trends), average_investigation_time_seconds=round(sum(item.snapshot.metadata.duration_seconds for item in records) / max(count, 1), 4), average_confidence=round(sum(item.snapshot.confidence.overall for item in records) / max(count, 1), 4), average_resolution_time_seconds=round(sum(item.snapshot.outcome.resolution_time_seconds or 0 for item in records) / max(count, 1), 4), outcome_distribution=dict(outcomes), resolution_success_rate=round(successful / max(count, 1), 4), false_positive_rate=round(false_positive / max(count, 1), 4), analyst_statistics=dict(analysts), historical_trends=dict(trends))
