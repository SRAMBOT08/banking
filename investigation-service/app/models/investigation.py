from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import uuid4
from pydantic import BaseModel, Field


class InvestigationState(str, Enum):
    NEW = "NEW"
    OPEN = "OPEN"
    COLLECTING_EVIDENCE = "COLLECTING_EVIDENCE"
    CORRELATING = "CORRELATING"
    ANALYZING = "ANALYZING"
    WAITING_FOR_EVIDENCE = "WAITING_FOR_EVIDENCE"
    READY_FOR_DECISION = "READY_FOR_DECISION"
    ESCALATED = "ESCALATED"
    DECIDED = "DECIDED"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    CLOSED = "CLOSED"
    ARCHIVED = "ARCHIVED"


class InvestigationPriority(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class TimelineEvent(BaseModel):
    event_id: str = Field(default_factory=lambda: str(uuid4()))
    timestamp: str
    event_type: str
    description: str
    evidence_refs: List[str] = Field(default_factory=list)
    source: str = "deterministic"


class InvestigationTimeline(BaseModel):
    events: List[TimelineEvent] = Field(default_factory=list)


class InvestigationConfidence(BaseModel):
    score: int = 0
    pattern_score: int = 0
    evidence_score: int = 0
    correlation_score: int = 0
    completeness_score: int = 0
    historical_score: int = 0
    explanation: List[str] = Field(default_factory=list)


class ConfidenceHistory(BaseModel):
    timestamp: str
    score: int
    reason: str


class InvestigationRecommendation(BaseModel):
    """Deprecated: Recommendations belong to Execution Service. Kept for API compatibility."""
    recommendation_id: str
    title: str
    required_evidence: List[str] = Field(default_factory=list)
    priority: InvestigationPriority = InvestigationPriority.MEDIUM
    source_pattern: Optional[str] = None


class MissingEvidence(BaseModel):
    evidence_type: str
    reason: str
    priority: InvestigationPriority = InvestigationPriority.MEDIUM
    blocked: bool = False


class Hypothesis(BaseModel):
    hypothesis_id: str = Field(default_factory=lambda: str(uuid4()))
    pattern_name: str
    pattern_version: str
    confidence: int
    candidate_ids: List[str] = Field(default_factory=list)
    matched_indicators: List[str] = Field(default_factory=list)
    missing_indicators: List[str] = Field(default_factory=list)
    mitre_mapping: Optional[Any] = None
    fraud_mapping: Optional[Any] = None
    explanation: Dict[str, Any] = Field(default_factory=dict)
    status: str = "active"


class InvestigationMetadata(BaseModel):
    tenant_id: str
    correlation_ids: List[str] = Field(default_factory=list)
    created_at: str
    updated_at: str
    source: str = "investigation-service"
    schema_version: str = "1.0"


# DEPRECATED: Evidence storage moved to Evidence Service
# TODO: Remove after API migration - kept for backward compatibility
class InvestigationEvidence(BaseModel):
    evidence_id: str
    evidence_type: str = "unknown"
    timestamp: Optional[str] = None
    confidence: int = 0
    properties: Dict[str, Any] = Field(default_factory=dict)
    source: str = "unknown"


# DEPRECATED: Evidence summary moved to Evidence Service
# TODO: Remove after API migration - kept for backward compatibility
class EvidenceSummary(BaseModel):
    total: int = 0
    by_type: Dict[str, int] = Field(default_factory=dict)
    average_confidence: int = 0
    evidence_ids: List[str] = Field(default_factory=list)


class InvestigationConfidence(BaseModel):
    score: int = 0
    pattern_score: int = 0
    evidence_score: int = 0
    correlation_score: int = 0
    completeness_score: int = 0
    historical_score: int = 0
    explanation: List[str] = Field(default_factory=list)


class ConfidenceHistory(BaseModel):
    timestamp: str
    score: int
    reason: str


# DEPRECATED: Recommendations moved to Execution Service
# TODO: Remove after API migration - kept for backward compatibility
class InvestigationRecommendation(BaseModel):
    recommendation_id: str
    title: str
    required_evidence: List[str] = Field(default_factory=list)
    priority: InvestigationPriority = InvestigationPriority.MEDIUM
    source_pattern: Optional[str] = None


class MissingEvidence(BaseModel):
    evidence_type: str
    reason: str
    priority: InvestigationPriority = InvestigationPriority.MEDIUM
    blocked: bool = False


class Investigation(BaseModel):
    investigation_id: str = Field(default_factory=lambda: str(uuid4()))
    state: InvestigationState = InvestigationState.NEW
    priority: InvestigationPriority = InvestigationPriority.LOW
    confidence: InvestigationConfidence = Field(default_factory=InvestigationConfidence)
    timeline: InvestigationTimeline = Field(default_factory=InvestigationTimeline)
    hypotheses: List[Hypothesis] = Field(default_factory=list)
    missing_evidence: List[MissingEvidence] = Field(default_factory=list)
    next_action: str = "Collect evidence"
    confidence_history: List[ConfidenceHistory] = Field(default_factory=list)
    metadata: InvestigationMetadata
    state_history: List[Dict[str, str]] = Field(default_factory=list)

    # DEPRECATED FIELDS - kept for API compatibility, scheduled for removal
    # Evidence storage moved to Evidence Service
    evidence: List[Any] = Field(default_factory=list, deprecated=True)
    evidence_summary: EvidenceSummary = Field(default_factory=EvidenceSummary, deprecated=True)
    related_entities: List[str] = Field(default_factory=list, deprecated=True)
    # Execution plans moved to Execution Service
    investigation_plan: List[InvestigationRecommendation] = Field(default_factory=list, deprecated=True)
    # AI reports moved to AI Report Service
    explanation: List[str] = Field(default_factory=list, deprecated=True)

    @classmethod
    def create(cls, tenant_id: str, correlation_ids: List[str], now: Optional[str] = None):
        timestamp = now or datetime.now(timezone.utc).isoformat()
        return cls(metadata=InvestigationMetadata(tenant_id=tenant_id, correlation_ids=correlation_ids,
                                                   created_at=timestamp, updated_at=timestamp))
