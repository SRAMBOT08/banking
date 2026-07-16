from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ThreatSummary(BaseModel):
    threat_id: str
    pattern_name: str
    pattern_version: str = "1.0"
    confidence: float = 0.0
    tenant_id: Optional[str] = None
    investigation_id: Optional[str] = None
    correlation_id: Optional[str] = None
    timestamp: Optional[str] = None


class ThreatDetails(ThreatSummary):
    explanation: Dict[str, Any] = Field(default_factory=dict)
    evidence_refs: List[Dict[str, Any]] = Field(default_factory=list)
    missing_evidence: List[Dict[str, Any]] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ThreatIndicator(BaseModel):
    id: str
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    weight: int = 0
    confidence: int = 100
    source: Optional[str] = None


class ThreatPattern(BaseModel):
    name: str
    version: str
    nodes: List[Dict[str, Any]] = Field(default_factory=list)
    edges: List[Dict[str, Any]] = Field(default_factory=list)
    metadata: Optional[Dict[str, Any]] = None
    recommendations: List[Dict[str, Any]] = Field(default_factory=list)
    mitre: Optional[Dict[str, Any]] = None
    fraud: Optional[Dict[str, Any]] = None
    related_patterns: List[str] = Field(default_factory=list)
    dependencies: List[str] = Field(default_factory=list)


class ThreatMetadata(BaseModel):
    registry_version: str = "1"
    validation_status: str = "unknown"
    source: str = "threat-intelligence-service"
    pattern_count: int = 0
    indicator_count: int = 0
    candidate_count: int = 0


class ThreatValidation(BaseModel):
    valid: bool
    errors: List[Dict[str, Any]] = Field(default_factory=list)
    warnings: List[Dict[str, Any]] = Field(default_factory=list)


class ThreatStatistics(BaseModel):
    pattern_count: int = 0
    indicator_count: int = 0
    threat_count: int = 0
    high_confidence_count: int = 0
    registry_version: str = "1"
    validation_status: str = "unknown"


class ThreatSearchRequest(BaseModel):
    query: Optional[str] = None
    investigation_id: Optional[str] = None
    tenant_id: Optional[str] = None
    correlation_id: Optional[str] = None
    pattern_name: Optional[str] = None
    min_confidence: Optional[float] = None
    offset: int = Field(default=0, ge=0)
    limit: int = Field(default=100, ge=1, le=1000)


class ThreatSearchResult(BaseModel):
    items: List[ThreatDetails] = Field(default_factory=list)
    total: int = 0
    offset: int = 0
    limit: int = 100
