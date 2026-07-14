from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, StrictStr, StrictInt, StrictFloat, validator

from ..enums.types import (
    EventType,
    Severity,
    Classification,
)


class BaseEvent(BaseModel):
    """Canonical base event for SentinelIQ.

    All domain events must inherit from this model. This BaseEvent enforces
    required metadata and validation rules used by platform components.
    """

    event_id: UUID = Field(default_factory=uuid4)
    event_type: EventType
    event_version: StrictStr = Field(..., description="Event contract version, semantic versioning")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    ingestion_timestamp: datetime = Field(default_factory=datetime.utcnow)
    correlation_id: Optional[UUID] = None
    investigation_id: Optional[UUID] = None
    tenant_id: StrictStr
    source_id: StrictStr
    producer_service: StrictStr
    schema_version: StrictStr = Field(default="1.0")
    trace_id: Optional[StrictStr] = None
    severity: Optional[Severity] = None
    classification: Optional[Classification] = None
    metadata: Dict[StrictStr, Any] = Field(default_factory=dict)

    class Config:
        use_enum_values = True
        validate_assignment = True

    @validator("tenant_id", "source_id", "producer_service")
    def non_empty_str(cls, v: str) -> str:  # type: ignore[override]
        if not v or not v.strip():
            raise ValueError("value must be a non-empty string")
        return v

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump()

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BaseEvent":
        return cls.model_validate(data)

    def to_json(self) -> str:
        return self.model_dump_json()

    @classmethod
    def from_json(cls, payload: str) -> "BaseEvent":
        return cls.model_validate_json(payload)
