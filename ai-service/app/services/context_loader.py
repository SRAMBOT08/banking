from __future__ import annotations
from copy import deepcopy
from typing import Any, Dict
from app.models.context import AIContext
from app.models.snapshot_contract import SnapshotDocument


class SnapshotContextLoader:
    """Loads only serialized Investigation Snapshots and produces AIContext."""

    def load(self, payload: SnapshotDocument | Dict[str, Any]) -> AIContext:
        snapshot = payload if isinstance(payload, SnapshotDocument) else SnapshotDocument.model_validate(deepcopy(payload))
        return AIContext.from_snapshot(snapshot)
