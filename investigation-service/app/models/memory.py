from __future__ import annotations
from datetime import datetime, timezone
from hashlib import sha256
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class InvestigationMemoryEvent(BaseModel):
    event_id: str
    investigation_id: str
    event_type: str
    timestamp: str
    sequence: int
    payload: Dict[str, Any] = Field(default_factory=dict)
    correlation_id: Optional[str] = None
    trace_id: Optional[str] = None
    tenant_id: Optional[str] = None

    @classmethod
    def create(cls, investigation_id: str, event_type: str, sequence: int, payload: Dict[str, Any], timestamp: Optional[str] = None, tenant_id: Optional[str] = None, correlation_id: Optional[str] = None, trace_id: Optional[str] = None):
        timestamp = timestamp or datetime.now(timezone.utc).isoformat()
        material = f"{investigation_id}|{event_type}|{sequence}|{timestamp}|{payload}"
        return cls(event_id=sha256(material.encode()).hexdigest()[:32], investigation_id=investigation_id,
                   event_type=event_type, timestamp=timestamp, sequence=sequence, payload=payload,
                   tenant_id=tenant_id, correlation_id=correlation_id, trace_id=trace_id)
