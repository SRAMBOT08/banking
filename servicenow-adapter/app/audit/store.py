from __future__ import annotations

import hashlib
import json
from pathlib import Path
from threading import RLock
from typing import List

from app.models import AuditRecord


class ImmutableAuditStore:
    def __init__(self, log_path: str):
        self.path = Path(log_path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._records: List[AuditRecord] = []
        self._lock = RLock()
        self._last_hash = ""

    def append(self, record: AuditRecord) -> str:
        with self._lock:
            payload = record.model_dump(mode="json")
            payload_json = json.dumps(payload, sort_keys=True, separators=(",", ":"))
            chained_hash = hashlib.sha256(f"{self._last_hash}:{payload_json}".encode("utf-8")).hexdigest()
            line = json.dumps({"record": payload, "hash": chained_hash}, sort_keys=True)
            with self.path.open("a", encoding="utf-8") as stream:
                stream.write(line + "\n")
            self._last_hash = chained_hash
            self._records.append(record)
            return chained_hash

    def list(self) -> List[AuditRecord]:
        with self._lock:
            return list(self._records)
