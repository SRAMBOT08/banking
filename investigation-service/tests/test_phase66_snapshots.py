from app.models.events import snapshot_metadata_event
from app.models.investigation import InvestigationState
from app.services.investigation_manager import InvestigationManager
from app.services.memory import InvestigationMemory
from app.services.snapshot_builder import SnapshotBuilder
from app.services.snapshot_diff import SnapshotDiffEngine
from app.services.snapshot_manager import SnapshotManager
from app.services.snapshot_metrics import SnapshotMetrics
from app.services.snapshot_repository import SnapshotRepository
from app.services.snapshot_serializer import SnapshotSerializer
from app.services.snapshot_validator import SnapshotValidator
from app.schemas.candidate import CandidateInput


def candidate(candidate_id="candidate-1", confidence=60, evidence_id="ev-1"):
    return CandidateInput(
        candidate_id=candidate_id,
        tenant_id="tenant-1",
        correlation_id="corr-1",
        pattern_name="account_takeover",
        pattern_version="1.0",
        confidence=confidence,
        timestamp="2026-01-01T09:00:00Z",
        evidence_refs=[{"id": evidence_id, "type": "login", "confidence": 80, "properties": {"user_id": "user-1"}}],
    )


def test_snapshot_is_complete_immutable_and_retrievable():
    memory = InvestigationMemory()
    manager = InvestigationManager(memory=memory)
    investigation = manager.process(candidate())
    snapshots = SnapshotManager(memory)
    first = snapshots.create(investigation, reason="investigation_created")

    assert first.metadata.snapshot_version == 1
    assert first.metadata.investigation_id == investigation.investigation_id
    assert first.evidence == investigation.evidence
    assert first.graph["nodes"]
    assert len(first.memory) == len(memory.list(investigation.investigation_id))
    assert SnapshotValidator().validate(first) == []

    investigation.evidence.clear()
    assert len(snapshots.latest(investigation.investigation_id).evidence) == 1
    assert first.related_entities == ["user_id:user-1"]


def test_snapshot_versioning_diff_and_deterministic_serialization():
    memory = InvestigationMemory()
    manager = InvestigationManager(memory=memory)
    investigation = manager.process(candidate())
    snapshots = SnapshotManager(memory)
    first = snapshots.create(investigation, reason="initial")

    manager.process(candidate("candidate-2", confidence=90, evidence_id="ev-2"))
    second = snapshots.create(manager.repository.get(investigation.investigation_id), reason="evidence_added")
    diff = SnapshotDiffEngine().compare(first, second)

    assert second.metadata.snapshot_version == 2
    assert second.metadata.parent_snapshot == first.metadata.snapshot_id
    assert [item.evidence_id for item in diff.added_evidence] == ["ev-2"]
    assert diff.confidence_changes["from"] != diff.confidence_changes["to"]
    serializer = SnapshotSerializer()
    assert serializer.serialize(second) == serializer.serialize(serializer.deserialize(serializer.serialize(second)))


def test_snapshot_repository_policy_metrics_and_metadata_event():
    memory = InvestigationMemory()
    manager = InvestigationManager(memory=memory)
    investigation = manager.process(candidate())
    snapshot_manager = SnapshotManager(memory)
    snapshot = snapshot_manager.create(investigation, reason="manual")

    assert len(snapshot_manager.list(investigation.investigation_id)) == 1
    assert snapshot_manager.history(investigation.investigation_id).versions[0].version == 1
    try:
        snapshot_manager.delete(investigation.investigation_id, 1)
    except PermissionError:
        pass
    else:
        raise AssertionError("snapshot deletion must be disabled by default")

    event = snapshot_metadata_event(snapshot)
    assert event.event_type == "INVESTIGATION_SNAPSHOT_CREATED"
    assert event.snapshot_version == 1
    stats = snapshot_manager.metrics.snapshot()
    assert stats.snapshot_count == 1
    assert stats.latest_version[investigation.investigation_id] == 1
