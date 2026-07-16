from __future__ import annotations
from datetime import datetime, timezone
from typing import Any
from uuid import UUID
from .models import AuditEntry, AuditSection, ProvenanceReference


class AuditManager:
    def build(self, *, case_id: UUID, version: int, metadata: Any, provenance: tuple[ProvenanceReference, ...], created_by: str, execution_metadata: dict[str, Any] | None = None) -> AuditSection:
        investigation_id = str(metadata.get('investigation_id', ''))
        now = datetime.now(timezone.utc)
        entry = AuditEntry(action='case_created', actor=created_by, occurred_at=now, investigation_id=investigation_id, case_id=case_id, version=version, details={'source_services': sorted({item.source_service for item in provenance})})
        return AuditSection(created_at=now, created_by=created_by, investigation_id=investigation_id, workflow_id=metadata.get('workflow_id'), decision_version=metadata.get('decision_version'), confidence_version=metadata.get('confidence_version'), source_services=tuple(sorted({item.source_service for item in provenance})), provenance=provenance, execution_metadata=execution_metadata or {}, entries=(entry,))
