from __future__ import annotations
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from app.core.logger import get_logger
from app.engine.confidence import aggregate_confidence
from app.engine.correlator import correlation_strength, entity_keys
from app.engine.deduplication import find_duplicate_hypothesis, merge_hypothesis
from app.engine.explainability import explain
from app.engine.missing_evidence import identify_missing_evidence
from app.engine.priority import assign_priority
from app.engine.state_machine import transition
from app.engine.timeline import add_timeline_event
from app.models.investigation import (Hypothesis, Investigation, InvestigationEvidence, InvestigationPriority,
                                      InvestigationState, TimelineEvent, ConfidenceHistory,
                                      InvestigationRecommendation)
from app.repositories.investigation_repository import InMemoryInvestigationRepository
from app.schemas.candidate import CandidateInput
from app.services.memory import InvestigationMemory
from app.services.policy import InvestigationPolicy

logger = get_logger("investigation_manager")


class InvestigationManager:
    def __init__(self, repository: Optional[InMemoryInvestigationRepository] = None,
                 memory: Optional[InvestigationMemory] = None,
                 policy: Optional[InvestigationPolicy] = None,
                 snapshot_manager=None):
        self.repository = repository or InMemoryInvestigationRepository()
        self.memory = memory or InvestigationMemory()
        self.policy = policy or InvestigationPolicy()
        self.snapshot_manager = snapshot_manager

    def set_snapshot_manager(self, snapshot_manager) -> None:
        self.snapshot_manager = snapshot_manager

    def _create_snapshot(self, investigation: Investigation, reason: str) -> None:
        if self.snapshot_manager is not None:
            self.snapshot_manager.create(investigation, reason=reason, related_investigations=self.repository.list_all())

    def _find_target(self, candidate: CandidateInput) -> Optional[Investigation]:
        if candidate.investigation_id:
            return self.repository.get(candidate.investigation_id)
        if candidate.correlation_id:
            matches = self.repository.find_by_correlation(candidate.correlation_id)
            if matches:
                return matches[0]
        incoming_keys = entity_keys(self._candidate_evidence(candidate))
        for investigation in self.repository.list_all():
            if incoming_keys and incoming_keys & entity_keys(investigation.evidence):
                return investigation
        return None

    @staticmethod
    def _candidate_evidence(candidate: CandidateInput) -> List[InvestigationEvidence]:
        result = []
        for index, item in enumerate(candidate.evidence_refs):
            if isinstance(item, str):
                result.append(InvestigationEvidence(evidence_id=item, source="candidate"))
            elif isinstance(item, dict):
                result.append(InvestigationEvidence(evidence_id=str(item.get("evidence_id") or item.get("id") or f"{candidate.candidate_id}:{index}"),
                                                     evidence_type=str(item.get("evidence_type") or item.get("type") or "unknown"),
                                                     timestamp=item.get("timestamp"), confidence=int(item.get("confidence", 0) or 0),
                                                     properties=item.get("properties", item), source="candidate"))
        return result

    def process(self, candidate: CandidateInput) -> Investigation:
        investigation = self._find_target(candidate)
        was_created = investigation is None
        now = datetime.now(timezone.utc).isoformat()
        if investigation is None:
            investigation = Investigation.create(candidate.tenant_id, [candidate.correlation_id] if candidate.correlation_id else [], now)
            investigation.state = transition(investigation.state, InvestigationState.OPEN)
            investigation.state_history.append({"from": InvestigationState.NEW.value, "to": InvestigationState.OPEN.value, "timestamp": now})
            self.memory.append(investigation, "INVESTIGATION_CREATED", {"state": investigation.state.value}, now)
            logger.info("investigation_created", extra={"investigation_id": investigation.investigation_id})
        elif candidate.correlation_id and candidate.correlation_id not in investigation.metadata.correlation_ids:
            investigation.metadata.correlation_ids.append(candidate.correlation_id)

        hypothesis = Hypothesis(pattern_name=candidate.pattern_name, pattern_version=candidate.pattern_version,
                                confidence=candidate.confidence, candidate_ids=[candidate.candidate_id],
                                matched_indicators=candidate.matched_indicators,
                                missing_indicators=candidate.missing_indicators,
                                mitre_mapping=candidate.mitre_mapping,
                                fraud_mapping=candidate.fraud_mapping,
                                explanation=candidate.explanation)
        duplicate = find_duplicate_hypothesis(investigation, hypothesis)
        if duplicate:
            merge_hypothesis(duplicate, hypothesis)
            self.memory.append(investigation, "HYPOTHESIS_UPDATED", duplicate.model_dump(), now)
        else:
            investigation.hypotheses.append(hypothesis)
            self.memory.append(investigation, "HYPOTHESIS_ADDED", hypothesis.model_dump(), now)

        for evidence in self._candidate_evidence(candidate):
            if not any(existing.evidence_id == evidence.evidence_id for existing in investigation.evidence):
                investigation.evidence.append(evidence)
                self.memory.append(investigation, "EVIDENCE_ADDED", evidence.model_dump(), now)
                logger.info("evidence_added", extra={"investigation_id": investigation.investigation_id, "evidence_id": evidence.evidence_id})
        investigation.evidence.sort(key=lambda item: (item.timestamp or "", item.evidence_id))
        investigation.related_entities = sorted(entity_keys(investigation.evidence))
        investigation.evidence_summary.total = len(investigation.evidence)
        investigation.evidence_summary.evidence_ids = [item.evidence_id for item in investigation.evidence]
        investigation.evidence_summary.by_type = {}
        for evidence in investigation.evidence:
            investigation.evidence_summary.by_type[evidence.evidence_type] = investigation.evidence_summary.by_type.get(evidence.evidence_type, 0) + 1
        investigation.evidence_summary.average_confidence = round(sum(item.confidence for item in investigation.evidence) / len(investigation.evidence)) if investigation.evidence else 0
        timeline_event = TimelineEvent(timestamp=candidate.timestamp, event_type="HYPOTHESIS_RECEIVED", description=f"Hypothesis received: {candidate.pattern_name}", evidence_refs=investigation.evidence_summary.evidence_ids)
        add_timeline_event(investigation, timeline_event)
        self.memory.append(investigation, "TIMELINE_UPDATED", timeline_event.model_dump(), candidate.timestamp)
        investigation.confidence = aggregate_confidence(investigation)
        investigation.confidence_history.append(ConfidenceHistory(timestamp=now, score=investigation.confidence.score, reason="Candidate aggregation"))
        self.memory.append(investigation, "CONFIDENCE_UPDATED", {
            **investigation.confidence.model_dump(), "timestamp": now, "reason": "Candidate aggregation"
        }, now)
        investigation.missing_evidence = identify_missing_evidence(investigation)
        self.memory.append(investigation, "MISSING_EVIDENCE_UPDATED", {"items": [item.model_dump() for item in investigation.missing_evidence]}, now)
        previous_priority = investigation.priority
        investigation.priority = assign_priority(investigation)
        if investigation.priority != previous_priority:
            self.memory.append(investigation, "PRIORITY_CHANGED", {"from": previous_priority.value, "to": investigation.priority.value}, now)
        investigation.next_action = "Collect missing evidence" if investigation.missing_evidence else "Prepare structured investigation context"
        investigation.explanation = explain(investigation)
        if candidate.recommendation:
            recommendation = candidate.recommendation if isinstance(candidate.recommendation, dict) else {"id": str(candidate.recommendation)}
            recommendation_id = str(recommendation.get("recommendation_id") or recommendation.get("id") or f"{candidate.pattern_name}:recommendation")
            if not any(item.recommendation_id == recommendation_id for item in investigation.investigation_plan):
                investigation.investigation_plan.append(InvestigationRecommendation(
                    recommendation_id=recommendation_id,
                    title=str(recommendation.get("title") or recommendation.get("name") or "Deterministic follow-up"),
                    required_evidence=list(recommendation.get("required_evidence", [])),
                    source_pattern=candidate.pattern_name,
                ))
                self.memory.append(investigation, "RECOMMENDATION_ADDED", investigation.investigation_plan[-1].model_dump(), now)
        if investigation.state == InvestigationState.OPEN:
            for target in (InvestigationState.CORRELATING, InvestigationState.ANALYZING):
                previous = investigation.state
                if not self.policy.validate_transition(previous, target):
                    raise ValueError(f"policy rejected transition: {previous.value}->{target.value}")
                investigation.state = transition(previous, target)
                investigation.state_history.append({"from": previous.value, "to": target.value, "timestamp": now})
                self.memory.append(investigation, "STATE_CHANGED", investigation.state_history[-1], now)
            target = InvestigationState.ESCALATED if self.policy.should_escalate(investigation) else (InvestigationState.WAITING_FOR_EVIDENCE if investigation.missing_evidence else InvestigationState.READY_FOR_AI)
            previous = investigation.state
            if not self.policy.validate_transition(previous, target):
                raise ValueError(f"policy rejected transition: {previous.value}->{target.value}")
            investigation.state = transition(previous, target)
            investigation.state_history.append({"from": previous.value, "to": target.value, "timestamp": now})
            self.memory.append(investigation, "STATE_CHANGED", investigation.state_history[-1], now)
            if target == InvestigationState.ESCALATED:
                self.memory.append(investigation, "POLICY_TRIGGERED", {"rule": "escalation_confidence_or_priority"}, now)
        investigation.metadata.updated_at = now
        self.repository.save(investigation)
        self._create_snapshot(investigation, "investigation_created" if was_created else "investigation_updated")
        logger.info("investigation_updated", extra={"investigation_id": investigation.investigation_id, "confidence": investigation.confidence.score, "priority": investigation.priority.value})
        return investigation

    def transition(self, investigation_id: str, target: InvestigationState) -> Investigation:
        investigation = self.repository.get(investigation_id)
        if investigation is None:
            raise KeyError(investigation_id)
        previous = investigation.state
        if not self.policy.validate_transition(previous, target):
            raise ValueError(f"policy rejected transition: {previous.value}->{target.value}")
        investigation.state = transition(previous, target)
        timestamp = datetime.now(timezone.utc).isoformat()
        investigation.state_history.append({"from": previous.value, "to": target.value, "timestamp": timestamp})
        self.memory.append(investigation, "STATE_CHANGED", investigation.state_history[-1], timestamp)
        investigation.metadata.updated_at = timestamp
        self.repository.save(investigation)
        self._create_snapshot(investigation, f"state_changed:{previous.value}->{target.value}")
        logger.info("state_transition", extra={"investigation_id": investigation_id, "from_state": previous.value, "to_state": target.value})
        return investigation

    def close(self, investigation_id: str) -> Investigation:
        return self.transition(investigation_id, InvestigationState.CLOSED)

    def reopen(self, investigation_id: str) -> Investigation:
        return self.transition(investigation_id, InvestigationState.OPEN)

    def list_all(self) -> List[Investigation]:
        return self.repository.list_all()
