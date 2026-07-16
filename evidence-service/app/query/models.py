from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class EvidenceSummary(BaseModel):
    evidence_id: str
    evidence_type: str = "unknown"
    source: str = "unknown"
    timestamp: Optional[str] = None
    confidence: float = 0.0

class EvidenceValidation(BaseModel):
    valid: bool
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)


class EvidenceDetails(EvidenceSummary):
    properties: Dict[str, Any] = Field(default_factory=dict)
    entity_ids: List[str] = Field(default_factory=list)


class EntityDetails(BaseModel):
    entity_id: str
    entity_type: str = "unknown"
    labels: List[str] = Field(default_factory=list)
    attributes: Dict[str, Any] = Field(default_factory=dict)
    evidence_ids: List[str] = Field(default_factory=list)


class RelationshipDetails(BaseModel):
    source_id: str
    target_id: str
    relationship_type: str
    properties: Dict[str, Any] = Field(default_factory=dict)


class EvidenceTimelineEntry(BaseModel):
    evidence_id: str
    timestamp: Optional[str] = None
    evidence_type: str = "unknown"
    source: str = "unknown"
    properties: Dict[str, Any] = Field(default_factory=dict)


class EvidenceTimeline(BaseModel):
    investigation_id: Optional[str] = None
    items: List[EvidenceTimelineEntry] = Field(default_factory=list)


class EvidenceStatistics(BaseModel):
    total_evidence: int = 0
    total_entities: int = 0
    total_relationships: int = 0
    by_type: Dict[str, int] = Field(default_factory=dict)
    by_source: Dict[str, int] = Field(default_factory=dict)


class EvidenceSearchResult(BaseModel):
    items: List[EvidenceDetails] = Field(default_factory=list)
    total: int = 0
    offset: int = 0
    limit: int = 100


class EvidenceQueryRequest(BaseModel):
    query: Optional[str] = None
    investigation_id: Optional[str] = None
    entity_id: Optional[str] = None
    correlation_id: Optional[str] = None
    evidence_type: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    offset: int = Field(default=0, ge=0)
    limit: int = Field(default=100, ge=1, le=1000)
