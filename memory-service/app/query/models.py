from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class CaseStatus(str, Enum):
    COMPLETED = "completed"
    CLOSED = "closed"
    REVIEWED = "reviewed"
    FALSE_POSITIVE = "false_positive"


class Severity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class OutcomeType(str, Enum):
    CONFIRMED_FRAUD = "confirmed_fraud"
    ACCOUNT_PROTECTED = "account_protected"
    FALSE_POSITIVE = "false_positive"
    UNDETERMINED = "undetermined"
    ESCALATED = "escalated"


class InvestigationSummary(BaseModel):
    investigation_id: str
    title: str
    summary: str = ""
    severity: Severity = Severity.MEDIUM
    case_status: CaseStatus = CaseStatus.COMPLETED
    fraud_category: Optional[str] = None
    root_cause: Optional[str] = None
    final_confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    mitre_mapping: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)


class InvestigationMetadata(BaseModel):
    tenant_id: str
    analyst_id: Optional[str] = None
    created_at: datetime
    completed_at: datetime
    duration_seconds: float = Field(ge=0.0)
    severity: Severity = Severity.MEDIUM
    case_status: CaseStatus = CaseStatus.COMPLETED
    source_system: str = "sentineliq"
    workflow_id: Optional[str] = None


class InvestigationOutcome(BaseModel):
    outcome_type: OutcomeType = OutcomeType.UNDETERMINED
    success: bool = False
    root_cause: Optional[str] = None
    resolution: Optional[str] = None
    resolution_time_seconds: Optional[float] = Field(default=None, ge=0.0)
    analyst_notes: str = ""
    completed_at: Optional[datetime] = None


class InvestigationDecision(BaseModel):
    decision: str
    rationale: str = ""
    approved: bool = False
    decision_at: Optional[datetime] = None
    policy_references: List[str] = Field(default_factory=list)


class InvestigationHypothesis(BaseModel):
    hypothesis_id: str
    description: str
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    selected: bool = False
    evidence_references: List[str] = Field(default_factory=list)
    threat_references: List[str] = Field(default_factory=list)
    knowledge_references: List[str] = Field(default_factory=list)
    graph_references: List[str] = Field(default_factory=list)


class InvestigationConfidence(BaseModel):
    overall: float = Field(default=0.0, ge=0.0, le=1.0)
    evidence: float = Field(default=0.0, ge=0.0, le=1.0)
    threat: float = Field(default=0.0, ge=0.0, le=1.0)
    knowledge: float = Field(default=0.0, ge=0.0, le=1.0)
    graph: float = Field(default=0.0, ge=0.0, le=1.0)
    historical: float = Field(default=0.0, ge=0.0, le=1.0)


class HistoricalEvidence(BaseModel):
    evidence_id: str
    evidence_type: str
    source: Optional[str] = None
    risk_score: Optional[float] = Field(default=None, ge=0.0, le=100.0)


class HistoricalThreat(BaseModel):
    threat_id: str
    pattern_name: str
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    references: List[str] = Field(default_factory=list)


class HistoricalKnowledge(BaseModel):
    knowledge_id: str
    category: Optional[str] = None
    version: Optional[str] = None
    references: List[str] = Field(default_factory=list)


class HistoricalGraph(BaseModel):
    node_ids: List[str] = Field(default_factory=list)
    relationship_ids: List[str] = Field(default_factory=list)
    community_id: Optional[str] = None
    centrality_score: Optional[float] = None


class InvestigationTimelineEvent(BaseModel):
    event_id: str
    event_type: str
    timestamp: datetime
    description: str = ""
    entity_id: Optional[str] = None
    properties: Dict[str, Any] = Field(default_factory=dict)


class InvestigationTimeline(BaseModel):
    investigation_id: str
    events: List[InvestigationTimelineEvent] = Field(default_factory=list)
    entity_id: Optional[str] = None
    timeline_type: str = "investigation"


class LessonsLearned(BaseModel):
    investigation_id: str
    lessons: List[str] = Field(default_factory=list)
    prevention_actions: List[str] = Field(default_factory=list)
    analyst_notes: str = ""


class ResolutionPattern(BaseModel):
    pattern_id: str
    name: str
    description: str = ""
    applicable_outcomes: List[OutcomeType] = Field(default_factory=list)
    success_rate: float = Field(default=0.0, ge=0.0, le=1.0)
    usage_count: int = Field(default=0, ge=0)


class InvestigationSnapshot(BaseModel):
    summary: InvestigationSummary
    metadata: InvestigationMetadata
    evidence_references: List[HistoricalEvidence] = Field(default_factory=list)
    threat_references: List[HistoricalThreat] = Field(default_factory=list)
    knowledge_references: List[HistoricalKnowledge] = Field(default_factory=list)
    graph_references: List[HistoricalGraph] = Field(default_factory=list)
    hypotheses: List[InvestigationHypothesis] = Field(default_factory=list)
    confidence: InvestigationConfidence = Field(default_factory=InvestigationConfidence)
    decision: Optional[InvestigationDecision] = None
    outcome: InvestigationOutcome = Field(default_factory=InvestigationOutcome)
    resolution: Optional[str] = None
    analyst_notes: str = ""
    lessons_learned: Optional[LessonsLearned] = None
    related_investigation_ids: List[str] = Field(default_factory=list)
    similarity_features: Dict[str, Any] = Field(default_factory=dict)
    timeline: InvestigationTimeline


class InvestigationRecord(BaseModel):
    snapshot: InvestigationSnapshot
    stored_at: datetime
    completed: bool = True


class InvestigationSimilarity(BaseModel):
    source_investigation_id: str
    matching_investigation_ids: List[str] = Field(default_factory=list)
    overall_score: float = Field(default=0.0, ge=0.0, le=1.0)
    feature_breakdown: Dict[str, float] = Field(default_factory=dict)
    matching_features: Dict[str, List[str]] = Field(default_factory=dict)
    explanations: List[str] = Field(default_factory=list)


class CaseSimilarity(BaseModel):
    investigation_id: str
    score: float = Field(ge=0.0, le=1.0)
    explanation: str = ""
    matching_features: List[str] = Field(default_factory=list)


class InvestigationSearchRequest(BaseModel):
    query: Optional[str] = None
    tenant_id: Optional[str] = None
    severity: Optional[Severity] = None
    case_status: Optional[CaseStatus] = None
    fraud_category: Optional[str] = None
    outcome_type: Optional[OutcomeType] = None
    mitre_mapping: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    offset: int = Field(default=0, ge=0)
    limit: int = Field(default=100, ge=1, le=1000)


class InvestigationSearchResponse(BaseModel):
    items: List[InvestigationSummary] = Field(default_factory=list)
    total: int = 0
    offset: int = 0
    limit: int = 100


class SimilarityRequest(BaseModel):
    investigation_id: Optional[str] = None
    tenant_id: Optional[str] = None
    evidence_types: List[str] = Field(default_factory=list)
    threat_patterns: List[str] = Field(default_factory=list)
    knowledge_references: List[str] = Field(default_factory=list)
    graph_references: List[str] = Field(default_factory=list)
    mitre_mapping: List[str] = Field(default_factory=list)
    fraud_category: Optional[str] = None
    outcome_type: Optional[OutcomeType] = None
    decision: Optional[str] = None
    resolution: Optional[str] = None
    risk_score: Optional[float] = Field(default=None, ge=0.0, le=100.0)
    confidence: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    limit: int = Field(default=10, ge=1, le=100)


class InvestigationStatistics(BaseModel):
    investigation_count: int = 0
    attack_frequency: Dict[str, int] = Field(default_factory=dict)
    investigation_frequency: Dict[str, int] = Field(default_factory=dict)
    average_investigation_time_seconds: float = 0.0
    average_confidence: float = 0.0
    average_resolution_time_seconds: float = 0.0
    outcome_distribution: Dict[str, int] = Field(default_factory=dict)
    resolution_success_rate: float = 0.0
    false_positive_rate: float = 0.0
    analyst_statistics: Dict[str, int] = Field(default_factory=dict)
    historical_trends: Dict[str, int] = Field(default_factory=dict)


class MemoryMetadata(BaseModel):
    service_version: str = "1.0"
    repository: str = "in-memory"
    completed_investigation_count: int = 0
    similarity_engine: str = "deterministic-feature-v1"
    timeline_engine: str = "deterministic-event-v1"
    last_updated: Optional[datetime] = None
