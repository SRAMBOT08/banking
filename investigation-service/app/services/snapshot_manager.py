from __future__ import annotations

from datetime import datetime, timezone
from time import perf_counter
from typing import Callable, Iterable, Optional

from app.core.logger import get_logger
from app.models.investigation import Investigation
from app.models.snapshot import InvestigationSnapshot, SnapshotDiff, SnapshotHistory
from app.services.snapshot_builder import SnapshotBuilder
from app.services.snapshot_diff import SnapshotDiffEngine
from app.services.snapshot_metrics import SnapshotMetrics
from app.services.snapshot_repository import SnapshotRepository
from app.services.snapshot_serializer import SnapshotSerializer
from app.services.snapshot_validator import SnapshotValidator
from app.services.snapshot_version import SnapshotVersionManager

logger = get_logger("snapshot_manager")


class SnapshotManager:
    def __init__(self, memory, repository: Optional[SnapshotRepository] = None,
                 builder: Optional[SnapshotBuilder] = None,
                 version_manager: Optional[SnapshotVersionManager] = None,
                 serializer: Optional[SnapshotSerializer] = None,
                 validator: Optional[SnapshotValidator] = None,
                 diff_engine: Optional[SnapshotDiffEngine] = None,
                 metrics: Optional[SnapshotMetrics] = None,
                 on_created: Optional[Callable[[InvestigationSnapshot], None]] = None):
        self.repository = repository or SnapshotRepository()
        self.builder = builder or SnapshotBuilder(memory)
        self.version_manager = version_manager or SnapshotVersionManager()
        self.serializer = serializer or SnapshotSerializer()
        self.validator = validator or SnapshotValidator()
        self.diff_engine = diff_engine or SnapshotDiffEngine()
        self.metrics = metrics or SnapshotMetrics(self.serializer)
        self.on_created = on_created

    def create(self, investigation: Investigation, reason: str = "manual",
               created_by: str = "investigation-service",
               related_investigations: Optional[Iterable[Investigation]] = None) -> InvestigationSnapshot:
        started = perf_counter()
        latest = self.repository.latest(investigation.investigation_id)
        version = self.version_manager.next_version(
            investigation.investigation_id,
            latest.metadata.snapshot_version if latest else None,
        )
        created_at = datetime.now(timezone.utc).isoformat()
        metadata = self.version_manager.metadata(
            investigation, version, created_at, reason,
            latest.metadata.snapshot_id if latest else None, created_by,
        )
        snapshot = self.builder.build(investigation, metadata, related_investigations)
        self.validator.assert_valid(snapshot)
        stored = self.repository.save(snapshot)
        elapsed = perf_counter() - started
        self.metrics.record(stored, elapsed)
        if self.on_created is not None:
            self.on_created(stored)
        logger.info("snapshot_created", extra={"investigation_id": investigation.investigation_id,
                                                "snapshot_id": stored.metadata.snapshot_id,
                                                "snapshot_version": version, "reason": reason})
        return stored

    def get(self, investigation_id: str, version: int) -> InvestigationSnapshot:
        snapshot = self.repository.get(investigation_id, version)
        if snapshot is None:
            raise KeyError(f"snapshot not found: {investigation_id}/{version}")
        logger.info("snapshot_loaded", extra={"investigation_id": investigation_id, "snapshot_version": version})
        return snapshot

    def list(self, investigation_id: str):
        snapshots = self.repository.list(investigation_id)
        logger.info("snapshot_retrieval", extra={"investigation_id": investigation_id, "count": len(snapshots)})
        return snapshots

    def latest(self, investigation_id: str) -> InvestigationSnapshot:
        snapshot = self.repository.latest(investigation_id)
        if snapshot is None:
            raise KeyError(f"snapshot not found: {investigation_id}")
        logger.info("snapshot_loaded", extra={"investigation_id": investigation_id,
                                                "snapshot_version": snapshot.metadata.snapshot_version})
        return snapshot

    def history(self, investigation_id: str) -> SnapshotHistory:
        return SnapshotHistory(investigation_id=investigation_id, versions=self.repository.history(investigation_id))

    def context(self, investigation_id: str, version: int):
        return self.get(investigation_id, version)

    def diff(self, investigation_id: str, from_version: int, to_version: int) -> SnapshotDiff:
        result = self.diff_engine.compare(self.get(investigation_id, from_version), self.get(investigation_id, to_version))
        logger.info("snapshot_compared", extra={"investigation_id": investigation_id,
                                                 "from_version": from_version, "to_version": to_version})
        return result

    def delete(self, investigation_id: str, version: int, allow: bool = False) -> bool:
        if not allow:
            raise PermissionError("snapshot deletion is disabled by policy")
        return self.repository.delete(investigation_id, version)
