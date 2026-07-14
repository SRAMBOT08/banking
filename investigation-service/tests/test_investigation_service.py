from app.engine.confidence import aggregate_confidence
from app.engine.priority import assign_priority
from app.engine.state_machine import can_transition
from app.models.investigation import Investigation, InvestigationEvidence, InvestigationPriority, InvestigationState
from app.repositories.investigation_repository import InMemoryInvestigationRepository
from app.schemas.candidate import CandidateInput
from app.services.investigation_manager import InvestigationManager


def candidate(candidate_id, pattern="account_takeover", confidence=84, correlation="corr-1", timestamp="2026-01-01T09:01:00Z"):
    return CandidateInput(candidate_id=candidate_id, tenant_id="tenant-1", correlation_id=correlation, pattern_name=pattern, pattern_version="1.0", confidence=confidence, timestamp=timestamp, evidence_refs=[{"id": "ev-1", "type": "login", "timestamp": timestamp, "confidence": 90, "properties": {"user_id": "u-1", "device_id": "d-1"}}])


def test_creation_correlation_and_deduplication():
    manager = InvestigationManager(InMemoryInvestigationRepository())
    first = manager.process(candidate("c-1"))
    second = manager.process(candidate("c-2", confidence=90))
    assert first.investigation_id == second.investigation_id
    assert len(second.hypotheses) == 1
    assert second.hypotheses[0].confidence == 90
    assert len(second.evidence) == 1


def test_timeline_is_sorted_and_confidence_is_deterministic():
    manager = InvestigationManager(InMemoryInvestigationRepository())
    investigation = manager.process(candidate("c-1", timestamp="2026-01-01T09:05:00Z"))
    manager.process(candidate("c-2", pattern="credential_stuffing", timestamp="2026-01-01T09:01:00Z"))
    result = manager.repository.get(investigation.investigation_id)
    assert [event.timestamp for event in result.timeline.events] == sorted(event.timestamp for event in result.timeline.events)
    assert result.confidence.score == aggregate_confidence(result).score


def test_priority_and_state_transitions():
    investigation = Investigation.create("tenant-1", [], "2026-01-01T00:00:00Z")
    investigation.evidence = [InvestigationEvidence(evidence_id="ev", confidence=100, properties={"financial_impact": 100000})]
    investigation.confidence.score = 90
    assert assign_priority(investigation) == InvestigationPriority.CRITICAL
    assert can_transition(InvestigationState.NEW, InvestigationState.OPEN)
    assert not can_transition(InvestigationState.NEW, InvestigationState.CLOSED)
