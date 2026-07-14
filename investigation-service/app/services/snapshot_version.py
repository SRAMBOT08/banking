from __future__ import annotations

from hashlib import sha256
from typing import Optional

from app.models.investigation import Investigation
from app.models.snapshot import SnapshotMetadata


class SnapshotVersionManager:
    def next_version(self, investigation_id: str, latest_version: Optional[int] = None) -> int:
        return (latest_version or 0) + 1

    def snapshot_id(self, investigation_id: str, version: int) -> str:
        return sha256(f"{investigation_id}|{version}".encode()).hexdigest()[:32]

    def investigation_version(self, investigation: Investigation) -> str:
        return investigation.metadata.updated_at

    def metadata(self, investigation: Investigation, version: int, created_at: str,
                 reason: str, parent_snapshot: Optional[str] = None,
                 created_by: str = "investigation-service") -> SnapshotMetadata:
        return SnapshotMetadata(
            snapshot_id=self.snapshot_id(investigation.investigation_id, version),
            snapshot_version=version,
            investigation_version=self.investigation_version(investigation),
            investigation_id=investigation.investigation_id,
            created_at=created_at,
            created_by=created_by,
            reason=reason,
            parent_snapshot=parent_snapshot,
        )
