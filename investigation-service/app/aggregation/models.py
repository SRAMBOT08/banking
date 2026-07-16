from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List
from pydantic import BaseModel, Field


class ContextMetadata(BaseModel):
    investigation_id: str
    tenant_id: str
    workflow_id: str | None = None
    correlation_id: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    aggregation_duration_ms: float = 0.0
    services_queried: List[str] = Field(default_factory=list)


class IntelligenceSection(BaseModel):
    items: List[Dict[str, Any]] = Field(default_factory=list)
    raw: Dict[str, Any] = Field(default_factory=dict)
    result_count: int = 0


class EvidenceContext(IntelligenceSection):
    pass


class ThreatContext(IntelligenceSection):
    pass


class KnowledgeContext(IntelligenceSection):
    pass


class GraphContext(IntelligenceSection):
    pass


class HistoricalContext(IntelligenceSection):
    pass


class RelatedEntity(BaseModel):
    id: str
    entity_type: str = "unknown"
    names: List[str] = Field(default_factory=list)
    sources: List[str] = Field(default_factory=list)


class RelatedEvidence(BaseModel):
    id: str
    evidence_type: str = "unknown"
    sources: List[str] = Field(default_factory=list)


class RelatedThreat(BaseModel):
    id: str
    name: str = "unknown"
    sources: List[str] = Field(default_factory=list)


class DataProvenance(BaseModel):
    source_id: str
    originating_service: str
    repository: str = "unknown"
    query_time: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    version: str = "v1"
    correlation_id: str
    investigation_id: str
    workflow_id: str | None = None
    confidence_source: str | None = None
    fact_type: str = "unknown"
    fact_id: str


class ConfidenceSource(BaseModel):
    source: str
    score: float | None = Field(default=None, ge=0.0, le=1.0)
    evidence_count: int = 0
    recorded_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class CorrelationRecord(BaseModel):
    left_source: str
    right_source: str
    left_id: str
    right_id: str
    relation: str
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    explanation: str = "deterministic identifier or feature correlation"


class CorrelationSummary(BaseModel):
    records: List[CorrelationRecord] = Field(default_factory=list)
    cross_service_references: Dict[str, List[str]] = Field(default_factory=dict)
    related_intelligence: List[str] = Field(default_factory=list)


class MergeStatistics(BaseModel):
    input_counts: Dict[str, int] = Field(default_factory=dict)
    output_counts: Dict[str, int] = Field(default_factory=dict)
    duplicates_removed: Dict[str, int] = Field(default_factory=dict)


class ValidationSummary(BaseModel):
    valid: bool = True
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)


class InvestigationContext(BaseModel):
    metadata: ContextMetadata
    evidence_context: EvidenceContext = Field(default_factory=EvidenceContext)
    threat_context: ThreatContext = Field(default_factory=ThreatContext)
    knowledge_context: KnowledgeContext = Field(default_factory=KnowledgeContext)
    graph_context: GraphContext = Field(default_factory=GraphContext)
    historical_context: HistoricalContext = Field(default_factory=HistoricalContext)
    related_entities: List[RelatedEntity] = Field(default_factory=list)
    related_evidence: List[RelatedEvidence] = Field(default_factory=list)
    related_threats: List[RelatedThreat] = Field(default_factory=list)
    mitre_mapping: List[str] = Field(default_factory=list)
    fraud_patterns: List[str] = Field(default_factory=list)
    recommendations: List[Dict[str, Any]] = Field(default_factory=list)
    timeline: List[Dict[str, Any]] = Field(default_factory=list)
    graph_relationships: List[Dict[str, Any]] = Field(default_factory=list)
    historical_similar_cases: List[Dict[str, Any]] = Field(default_factory=list)
    similarity_results: List[Dict[str, Any]] = Field(default_factory=list)
    confidence_sources: List[ConfidenceSource] = Field(default_factory=list)
    provenance: List[DataProvenance] = Field(default_factory=list)
    correlation_summary: CorrelationSummary = Field(default_factory=CorrelationSummary)
    missing_information: List[str] = Field(default_factory=list)
    validation: ValidationSummary = Field(default_factory=ValidationSummary)
    merge_statistics: MergeStatistics = Field(default_factory=MergeStatistics)
    context_metadata: Dict[str, Any] = Field(default_factory=dict)
    execution_metadata: Dict[str, Any] = Field(default_factory=dict)
