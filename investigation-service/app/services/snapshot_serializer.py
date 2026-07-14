from __future__ import annotations

import json
from hashlib import sha256
from typing import Any

from app.models.snapshot import InvestigationSnapshot


class SnapshotSerializer:
    def serialize(self, snapshot: InvestigationSnapshot) -> bytes:
        return self.to_json(snapshot).encode("utf-8")

    def to_json(self, snapshot: InvestigationSnapshot) -> str:
        return json.dumps(snapshot.model_dump(mode="json"), sort_keys=True, separators=(",", ":"))

    def checksum(self, snapshot: InvestigationSnapshot) -> str:
        return sha256(self.serialize(snapshot)).hexdigest()

    def deserialize(self, payload: bytes | str) -> InvestigationSnapshot:
        data = payload.decode("utf-8") if isinstance(payload, bytes) else payload
        return InvestigationSnapshot.model_validate_json(data)
