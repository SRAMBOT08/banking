from __future__ import annotations
import hashlib
import json
from datetime import datetime, timezone
from typing import Any
from uuid import UUID, uuid4
from .models import CaseFile, VersionMetadata


class CaseVersionManager:
    def content_hash(self, case: CaseFile | dict[str, Any]) -> str:
        payload = case.model_dump(mode='json') if hasattr(case, 'model_dump') else case
        payload = dict(payload); payload.pop('version', None)
        return hashlib.sha256(json.dumps(payload, sort_keys=True, default=str).encode()).hexdigest()

    def create(self, *, case: CaseFile, version: int, created_by: str, parent_version: int | None = None, change_summary: str = 'case build') -> VersionMetadata:
        return VersionMetadata(version=version, version_id=uuid4(), created_at=datetime.now(timezone.utc), created_by=created_by, parent_version=parent_version, change_summary=change_summary, content_hash=self.content_hash(case))

    def compare(self, left: CaseFile, right: CaseFile) -> dict[str, Any]:
        a, b = left.model_dump(mode='json'), right.model_dump(mode='json')
        changes = {}
        for key in sorted(set(a) | set(b)):
            if key != 'version' and a.get(key) != b.get(key): changes[key] = {'before': a.get(key), 'after': b.get(key)}
        return {'changed': bool(changes), 'changes': changes}
