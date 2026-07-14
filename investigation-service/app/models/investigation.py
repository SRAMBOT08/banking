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
    READY_FOR_AI = "READY_FOR_AI"
    ESCALATED = "ESCALATED"
    RESOLVED = "RESOLVED"
    CLOSED = "CLOSED"


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


class InvestigationEvidence(BaseModel):
    evidence_id: str
    evidence_type: str = "unknown"
    timestamp: Optional[str] = None
    confidence: int = 0
    properties: Dict[str, Any] = Field(default_factory=dict)
    source: str = "unknown"


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


class InvestigationMetadata(BaseModel):
    tenant_id: str
    correlation_ids: List[str] = Field(default_factory=list)
    created_at: str
    updated_at: str
    source: str = "investigation-service"
    schema_version: str = "1.0"


class Investigation(BaseModel):
    investigation_id: str = Field(default_factory=lambda: str(uuid4()))
    state: InvestigationState = InvestigationState.NEW
    priority: InvestigationPriority = InvestigationPriority.LOW
    confidence: InvestigationConfidence = Field(default_factory=InvestigationConfidence)
    timeline: InvestigationTimeline = Field(default_factory=InvestigationTimeline)
    evidence_summary: EvidenceSummary = Field(default_factory=EvidenceSummary)
    hypotheses: List[Hypothesis] = Field(default_factory=list)
    evidence: List[InvestigationEvidence] = Field(default_factory=list)
    related_entities: List[str] = Field(default_factory=list)
    missing_evidence: List[MissingEvidence] = Field(default_factory=list)
    investigation_plan: List[InvestigationRecommendation] = Field(default_factory=list)
    next_action: str = "Collect evidence"
    explanation: List[str] = Field(default_factory=list)
    confidence_history: List[ConfidenceHistory] = Field(default_factory=list)
    metadata: InvestigationMetadata
    state_history: List[Dict[str, str]] = Field(default_factory=list)
    actions: List[str] = Field(default_factory=list)

    @classmethod
    def create(cls, tenant_id: str, correlation_ids: List[str], now: Optional[str] = None):
        timestamp = now or datetime.now(timezone.utc).isoformat()
        return cls(metadata=InvestigationMetadata(tenant_id=tenant_id, correlation_ids=correlation_ids,
                                                   created_at=timestamp, updated_at=timestamp))
