from __future__ import annotations
from datetime import datetime
from typing import Any
from uuid import UUID
from pydantic import BaseModel, Field
from ..models import CaseFile, CaseStatistics


class CaseSearchQuery(BaseModel):
    investigation_id: str | None = None
    customer_id: str | None = None
    severity: str | None = None
    decision: str | None = None
    min_confidence: float | None = Field(default=None, ge=0, le=1)
    from_date: datetime | None = None
    to_date: datetime | None = None


class CaseSearchResult(BaseModel):
    items: list[CaseFile]
    total: int


class CaseStatisticsResponse(BaseModel):
    statistics: CaseStatistics
    case_count: int


class CaseHistoryResponse(BaseModel):
    case_id: UUID
    current_version: int
    versions: list[dict[str, Any]]
