from __future__ import annotations
from hashlib import sha256
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field
from app.models.investigation import Investigation
from app.models.snapshot import InvestigationSnapshot, SnapshotMetadataEvent


class InvestigationEvent(BaseModel):
    event_id: str
    event_type: str
    schema_version: str = "1.0"
    timestamp: str
    investigation_id: str
    tenant_id: str
    correlation_id: Optional[str] = None
    trace_id: Optional[str] = None
    payload: Investigation
    metadata: Dict[str, Any] = Field(default_factory=dict)

    @classmethod
    def from_investigation(cls, event_type: str, investigation: Investigation, timestamp: str, correlation_id: Optional[str] = None, trace_id: Optional[str] = None):
        material = f"{event_type}|{investigation.investigation_id}|{timestamp}|{investigation.metadata.updated_at}"
        return cls(event_id=sha256(material.encode()).hexdigest()[:32], event_type=event_type, timestamp=timestamp,
                   investigation_id=investigation.investigation_id, tenant_id=investigation.metadata.tenant_id,
                   correlation_id=correlation_id, trace_id=trace_id, payload=investigation)


def snapshot_metadata_event(snapshot: InvestigationSnapshot) -> SnapshotMetadataEvent:
    metadata = snapshot.metadata
    material = f"INVESTIGATION_SNAPSHOT_CREATED|{metadata.investigation_id}|{metadata.snapshot_version}|{metadata.created_at}"
    return SnapshotMetadataEvent(
        event_id=sha256(material.encode()).hexdigest()[:32],
        investigation_id=metadata.investigation_id,
        snapshot_id=metadata.snapshot_id,
        snapshot_version=metadata.snapshot_version,
        timestamp=metadata.created_at,
        tenant_id=snapshot.investigation.metadata.tenant_id,
        reason=metadata.reason,
        parent_snapshot=metadata.parent_snapshot,
        metadata={"created_by": metadata.created_by, "investigation_version": metadata.investigation_version},
    )
