from __future__ import annotations

from datetime import datetime, timedelta, timezone
import json
from typing import Iterable, List, Optional

from .engines import DeterministicSimilarityEngine, InvestigationStatisticsEngine, InvestigationTimelineEngine
from .models import *
from .repository import InvestigationMemoryRepository


class InMemoryInvestigationMemoryRepository(InvestigationMemoryRepository):
    """Reference repository containing completed investigation snapshots only."""

    def __init__(self, records: Optional[Iterable[InvestigationRecord]] = None):
        self._records = {record.snapshot.summary.investigation_id: record for record in (records or self._seed()) if record.completed}
        self._similarity = DeterministicSimilarityEngine()
        self._timeline = InvestigationTimelineEngine()
        self._statistics = InvestigationStatisticsEngine()

    @staticmethod
    def _seed() -> list[InvestigationRecord]:
        now = datetime.now(timezone.utc)

        def record(investigation_id: str, category: str, outcome: OutcomeType, success: bool, confidence: float, days_ago: int, evidence_type: str, threat: str, mitre: str, resolution: str, related: list[str], analyst: str) -> InvestigationRecord:
            completed = now - timedelta(days=days_ago)
            event = InvestigationTimelineEvent(event_id=f"{investigation_id}:completed", event_type="investigation_completed", timestamp=completed, description=f"Investigation {investigation_id} completed", entity_id="account-001")
            summary = InvestigationSummary(investigation_id=investigation_id, title=f"{category.replace('_', ' ').title()} Investigation", summary=f"Historical investigation for {category}.", severity=Severity.HIGH, case_status=CaseStatus.CLOSED, fraud_category=category, root_cause="Compromised access credential", final_confidence=confidence, mitre_mapping=[mitre], tags=[category, "historical"])
            snapshot = InvestigationSnapshot(summary=summary, metadata=InvestigationMetadata(tenant_id="tenant-1", analyst_id=analyst, created_at=completed - timedelta(seconds=420), completed_at=completed, duration_seconds=420, severity=Severity.HIGH, case_status=CaseStatus.CLOSED), evidence_references=[HistoricalEvidence(evidence_id=f"{investigation_id}:evidence", evidence_type=evidence_type, source="evidence-service", risk_score=82)], threat_references=[HistoricalThreat(threat_id=f"{investigation_id}:threat", pattern_name=threat, confidence=confidence)], knowledge_references=[HistoricalKnowledge(knowledge_id="pattern.account_takeover", category="generic", version="1.0")], graph_references=[HistoricalGraph(node_ids=["account-001", "device-001"], relationship_ids=["rel.user.device1"], community_id="community:account-001", centrality_score=0.71)], hypotheses=[InvestigationHypothesis(hypothesis_id=f"{investigation_id}:hypothesis", description="Account takeover", confidence=confidence, selected=True, evidence_references=[f"{investigation_id}:evidence"], threat_references=[f"{investigation_id}:threat"])], confidence=InvestigationConfidence(overall=confidence, evidence=0.9, threat=confidence, knowledge=0.85, graph=0.71, historical=0.65), decision=InvestigationDecision(decision="protect_account", rationale="Risk confirmed by multiple deterministic intelligence sources", approved=True, decision_at=completed), outcome=InvestigationOutcome(outcome_type=outcome, success=success, root_cause="Compromised access credential", resolution=resolution, resolution_time_seconds=180, analyst_notes="Completed and reviewed", completed_at=completed), resolution=resolution, analyst_notes="Historical case retained for future intelligence.", lessons_learned=LessonsLearned(investigation_id=investigation_id, lessons=["Shared devices and IPs are strong takeover indicators"], prevention_actions=["Require step-up authentication", "Review active sessions"]), related_investigation_ids=related, similarity_features={"risk_score": 82.0, "entity_ids": ["account-001", "device-001"]}, timeline=InvestigationTimeline(investigation_id=investigation_id, events=[event]))
            return InvestigationRecord(snapshot=snapshot, stored_at=completed, completed=True)

        return [
            record("investigation-history-001", "account_takeover", OutcomeType.ACCOUNT_PROTECTED, True, 0.88, 30, "authentication_event", "Account Takeover", "T1078", "Revoke sessions and require step-up authentication", ["investigation-history-002"], "analyst-1"),
            record("investigation-history-002", "account_takeover", OutcomeType.CONFIRMED_FRAUD, True, 0.93, 90, "authentication_event", "Account Takeover", "T1078", "Protect account and block suspicious IP", ["investigation-history-001"], "analyst-2"),
            record("investigation-history-003", "payment_fraud", OutcomeType.FALSE_POSITIVE, False, 0.61, 120, "transaction", "Suspicious Transaction", "T1566", "Close as false positive", [], "analyst-1"),
        ]

    def find_investigation(self, investigation_id: str) -> Optional[InvestigationRecord]:
        return self._records.get(investigation_id)

    def find_similar(self, request: SimilarityRequest) -> InvestigationSimilarity:
        if request.investigation_id in self._records:
            source = self._records[request.investigation_id].snapshot
            request = request.model_copy(update={
                "evidence_types": [item.evidence_type for item in source.evidence_references],
                "threat_patterns": [item.pattern_name for item in source.threat_references],
                "knowledge_references": [item.knowledge_id for item in source.knowledge_references],
                "graph_references": [item.community_id for item in source.graph_references if item.community_id],
                "mitre_mapping": source.summary.mitre_mapping,
                "fraud_category": source.summary.fraud_category,
                "outcome_type": source.outcome.outcome_type,
                "decision": source.decision.decision if source.decision else None,
                "resolution": source.resolution,
                "risk_score": source.similarity_features.get("risk_score"),
                "confidence": source.confidence.overall,
            })
        return self._similarity.compare(request, self._records.values())

    def find_historical_cases(self, request: InvestigationSearchRequest) -> InvestigationSearchResponse:
        records = list(self._records.values())
        if request.tenant_id:
            records = [item for item in records if item.snapshot.metadata.tenant_id == request.tenant_id]
        if request.severity:
            records = [item for item in records if item.snapshot.summary.severity == request.severity]
        if request.case_status:
            records = [item for item in records if item.snapshot.summary.case_status == request.case_status]
        if request.fraud_category:
            records = [item for item in records if item.snapshot.summary.fraud_category == request.fraud_category]
        if request.outcome_type:
            records = [item for item in records if item.snapshot.outcome.outcome_type == request.outcome_type]
        if request.mitre_mapping:
            wanted = {value.casefold() for value in request.mitre_mapping}
            records = [item for item in records if wanted.intersection(value.casefold() for value in item.snapshot.summary.mitre_mapping)]
        if request.tags:
            wanted = {value.casefold() for value in request.tags}
            records = [item for item in records if wanted.intersection(value.casefold() for value in item.snapshot.summary.tags)]
        if request.query:
            query = request.query.casefold()
            records = [item for item in records if query in json.dumps(item.snapshot.model_dump(mode="json"), default=str).casefold()]
        total = len(records)
        summaries = [item.snapshot.summary for item in records[request.offset:request.offset + request.limit]]
        return InvestigationSearchResponse(items=summaries, total=total, offset=request.offset, limit=request.limit)

    search = find_historical_cases

    def find_timeline(self, entity_id: str, timeline_type: str = "entity") -> InvestigationTimeline:
        record = self._records.get(entity_id)
        if record:
            return self._timeline.investigation(record)
        return self._timeline.entity(self._records.values(), entity_id, timeline_type)

    def find_outcome(self, investigation_id: str):
        record = self._records.get(investigation_id)
        return record.snapshot.outcome if record else None

    def find_resolution(self, investigation_id: str):
        record = self._records.get(investigation_id)
        if not record or not record.snapshot.resolution:
            return None
        outcome = record.snapshot.outcome.outcome_type
        return ResolutionPattern(pattern_id=f"resolution:{investigation_id}", name=record.snapshot.resolution, description="Historical successful resolution pattern", applicable_outcomes=[outcome], success_rate=float(record.snapshot.outcome.success), usage_count=1)

    def find_lessons_learned(self, investigation_id: str):
        record = self._records.get(investigation_id)
        return record.snapshot.lessons_learned if record else None

    def find_related(self, investigation_id: str):
        record = self._records.get(investigation_id)
        if not record:
            return []
        return [self._records[item].snapshot.summary for item in record.snapshot.related_investigation_ids if item in self._records]

    def find_historical_evidence(self, investigation_id: str):
        record = self._records.get(investigation_id)
        return record.snapshot.evidence_references if record else []

    def find_historical_threat(self, investigation_id: str):
        record = self._records.get(investigation_id)
        return record.snapshot.threat_references if record else []

    def find_historical_knowledge(self, investigation_id: str):
        record = self._records.get(investigation_id)
        return record.snapshot.knowledge_references if record else []

    def find_historical_graph(self, investigation_id: str):
        record = self._records.get(investigation_id)
        return record.snapshot.graph_references if record else []

    def statistics(self):
        return self._statistics.calculate(self._records.values())

    def metadata(self):
        return MemoryMetadata(completed_investigation_count=len(self._records), last_updated=datetime.now(timezone.utc))
