from __future__ import annotations

from copy import deepcopy
from threading import RLock
from typing import Dict, List, Optional

from app.models.snapshot import InvestigationSnapshot, SnapshotVersion


class SnapshotRepository:
    """Thread-safe process-local repository that never exposes stored mutable objects."""

    def __init__(self):
        self._snapshots: Dict[str, Dict[int, InvestigationSnapshot]] = {}
        self._lock = RLock()

    def save(self, snapshot: InvestigationSnapshot) -> InvestigationSnapshot:
        with self._lock:
            versions = self._snapshots.setdefault(snapshot.metadata.investigation_id, {})
            if snapshot.metadata.snapshot_version in versions:
                raise ValueError("snapshot version already exists")
            versions[snapshot.metadata.snapshot_version] = deepcopy(snapshot)
            return deepcopy(snapshot)

    def get(self, investigation_id: str, version: int) -> Optional[InvestigationSnapshot]:
        with self._lock:
            snapshot = self._snapshots.get(investigation_id, {}).get(int(version))
            return deepcopy(snapshot) if snapshot is not None else None

    def list(self, investigation_id: str) -> List[InvestigationSnapshot]:
        with self._lock:
            return [deepcopy(self._snapshots[investigation_id][version])
                    for version in sorted(self._snapshots.get(investigation_id, {}))]

    def latest(self, investigation_id: str) -> Optional[InvestigationSnapshot]:
        with self._lock:
            versions = self._snapshots.get(investigation_id, {})
            if not versions:
                return None
            return deepcopy(versions[max(versions)])

    def delete(self, investigation_id: str, version: int) -> bool:
        with self._lock:
            versions = self._snapshots.get(investigation_id, {})
            if int(version) not in versions:
                return False
            del versions[int(version)]
            if not versions:
                self._snapshots.pop(investigation_id, None)
            return True

    def history(self, investigation_id: str) -> List[SnapshotVersion]:
        return [SnapshotVersion(snapshot_id=item.metadata.snapshot_id,
                                investigation_id=item.metadata.investigation_id,
                                version=item.metadata.snapshot_version,
                                created_at=item.metadata.created_at,
                                parent_snapshot=item.metadata.parent_snapshot)
                for item in self.list(investigation_id)]
