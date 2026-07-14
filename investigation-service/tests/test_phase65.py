from app.engine.graph import build_investigation_graph, find_related
from app.models.events import InvestigationEvent
from app.models.investigation import Investigation, InvestigationState
from app.services.context_builder import InvestigationContextBuilder
from app.services.memory import InvestigationMemory
from app.services.metrics import InvestigationMetricsEngine
from app.services.policy import InvestigationPolicy
from app.services.replay import InvestigationReplay
from app.services.investigation_manager import InvestigationManager
from app.schemas.candidate import CandidateInput


def make_candidate():
    return CandidateInput(candidate_id="candidate-1", tenant_id="tenant-1", correlation_id="corr-1", pattern_name="account_takeover", pattern_version="1.0", confidence=90, timestamp="2026-01-01T09:00:00Z", evidence_refs=[])


def test_memory_context_graph_and_replay_are_consistent():
    memory = InvestigationMemory()
    manager = InvestigationManager(memory=memory)
    investigation = manager.process(make_candidate())
    events = memory.list(investigation.investigation_id)
    assert [event.sequence for event in events] == list(range(1, len(events) + 1))
    graph = build_investigation_graph(investigation)
    assert find_related(graph, investigation.investigation_id)
    context = InvestigationContextBuilder(memory).build(investigation)
    assert context.investigation.investigation_id == investigation.investigation_id
    assert len(context.memory) == len(events)
    replayed = InvestigationReplay(memory).replay(investigation)
    assert replayed.confidence_history == investigation.confidence_history


def test_policy_metrics_and_typed_event():
    investigation = Investigation.create("tenant-1", [], "2026-01-01T00:00:00+00:00")
    investigation.state = InvestigationState.OPEN
    policy = InvestigationPolicy(escalation_confidence=80)
    investigation.confidence.score = 90
    assert policy.should_escalate(investigation)
    metrics = InvestigationMetricsEngine().snapshot([investigation])
    assert metrics.open_investigations == 1
    event = InvestigationEvent.from_investigation("INVESTIGATION_UPDATED", investigation, "2026-01-01T00:01:00+00:00")
    serialized = event.model_dump_json()
    assert event.schema_version == "1.0"
    assert event.event_id == InvestigationEvent.model_validate_json(serialized).event_id
