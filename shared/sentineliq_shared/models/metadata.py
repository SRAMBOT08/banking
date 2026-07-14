from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, StrictStr


class SourceMetadata(BaseModel):
    source_id: StrictStr
    source_type: StrictStr
    source_name: Optional[StrictStr] = None
    last_ingest_at: Optional[datetime] = None


class CorrelationMetadata(BaseModel):
    correlation_id: Optional[UUID] = None
    trace_id: Optional[StrictStr] = None


class InvestigationMetadata(BaseModel):
    investigation_id: Optional[UUID] = None
    hypothesis_id: Optional[StrictStr] = None


class TenantMetadata(BaseModel):
    tenant_id: StrictStr
    org_id: Optional[StrictStr] = None


class TraceMetadata(BaseModel):
    trace_id: Optional[StrictStr] = None
    span_id: Optional[StrictStr] = None
