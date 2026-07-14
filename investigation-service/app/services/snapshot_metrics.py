from __future__ import annotations

from datetime import datetime, timezone
from typing import Iterable

from app.models.snapshot import InvestigationSnapshot, SnapshotStatistics
from app.services.snapshot_serializer import SnapshotSerializer


class SnapshotMetrics:
    def __init__(self, serializer: SnapshotSerializer | None = None):
        self.serializer = serializer or SnapshotSerializer()
        self._created = []

    def record(self, snapshot: InvestigationSnapshot, elapsed_seconds: float = 0.0) -> None:
        self._created.append((snapshot, float(elapsed_seconds)))

    def snapshot(self, snapshots: Iterable[InvestigationSnapshot] | None = None) -> SnapshotStatistics:
        items = list(snapshots if snapshots is not None else (item[0] for item in self._created))
        if not items:
            return SnapshotStatistics()
        grouped = {}
        latest = {}
        oldest = {}
        for item in items:
            investigation_id = item.metadata.investigation_id
            grouped[investigation_id] = grouped.get(investigation_id, 0) + 1
            latest[investigation_id] = max(latest.get(investigation_id, 0), item.metadata.snapshot_version)
            oldest[investigation_id] = min(oldest.get(investigation_id, item.metadata.snapshot_version), item.metadata.snapshot_version)
        elapsed = [duration for _, duration in self._created]
        return SnapshotStatistics(
            snapshot_count=len(items),
            average_snapshot_size=round(sum(len(self.serializer.serialize(item)) for item in items) / len(items), 2),
            average_snapshot_time_seconds=round(sum(elapsed) / len(elapsed), 6) if elapsed else 0.0,
            snapshots_per_investigation=grouped,
            latest_version=latest,
            oldest_version=oldest,
        )
