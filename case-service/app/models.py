from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Literal
from uuid import UUID, uuid4
from pydantic import BaseModel, ConfigDict, Field


class ImmutableModel(BaseModel):
    model_config = ConfigDict(frozen=True, extra='forbid')


class ProvenanceReference(ImmutableModel):
    source_service: str
    source_id: str | None = None
    source_version: str | None = None
    source_path: str | None = None
    originating_at: datetime | None = None
    correlation_id: str | None = None
    investigation_id: str | None = None


class CaseMetadata(ImmutableModel):
    case_id: UUID
    investigation_id: str
    tenant_id: str
    workflow_id: str | None = None
    correlation_id: str
    title: str
    status: str = 'completed'
    severity: str = 'unknown'
    customer_id: str | None = None
    account_ids: tuple[str, ...] = ()
    created_at: datetime
    created_by: str
    source_services: tuple[str, ...] = ()
    tags: tuple[str, ...] = ()


class CaseSummary(ImmutableModel):
    title: str
    description: str
    risk_level: str = 'unknown'
    key_findings: tuple[str, ...] = ()
    provenance: tuple[ProvenanceReference, ...] = ()


class ExecutiveSummary(CaseSummary):
    audience: Literal['executive'] = 'executive'


class TechnicalSummary(CaseSummary):
    audience: Literal['technical'] = 'technical'
    indicators: tuple[dict[str, Any], ...] = ()


class SectionBase(ImmutableModel):
    items: tuple[dict[str, Any], ...] = ()
    summary: str = ''
    provenance: tuple[ProvenanceReference, ...] = ()


class EvidenceSection(SectionBase):
    source_service: str = 'evidence-intelligence-service'


class ThreatSection(SectionBase):
    source_service: str = 'threat-intelligence-service'
    mitre_mapping: tuple[str, ...] = ()
    fraud_classification: tuple[str, ...] = ()


class KnowledgeSection(SectionBase):
    source_service: str = 'knowledge-service'


class GraphSection(SectionBase):
    source_service: str = 'graph-intelligence-service'
    relationships: tuple[dict[str, Any], ...] = ()


class HistoricalSection(SectionBase):
    source_service: str = 'investigation-memory-service'
    similar_cases: tuple[dict[str, Any], ...] = ()


class TimelineSection(SectionBase):
    events: tuple[dict[str, Any], ...] = ()


class HypothesisSection(SectionBase):
    hypotheses: tuple[dict[str, Any], ...] = ()


class ConfidenceSection(SectionBase):
    sources: tuple[dict[str, Any], ...] = ()
    final_score: float | None = None


class DecisionSection(SectionBase):
    decision: dict[str, Any] = Field(default_factory=dict)
    decision_version: str | None = None


class RecommendationSection(SectionBase):
    recommendations: tuple[dict[str, Any], ...] = ()


class ExecutionSection(SectionBase):
    plan: dict[str, Any] = Field(default_factory=dict)
    execution_metadata: dict[str, Any] = Field(default_factory=dict)


class ReferenceSection(ImmutableModel):
    references: tuple[dict[str, Any], ...] = ()
    provenance: tuple[ProvenanceReference, ...] = ()


class AttachmentSection(ImmutableModel):
    attachments: tuple[dict[str, Any], ...] = ()
    provenance: tuple[ProvenanceReference, ...] = ()


class AuditEntry(ImmutableModel):
    action: str
    actor: str
    occurred_at: datetime
    investigation_id: str
    case_id: UUID
    version: int
    details: dict[str, Any] = Field(default_factory=dict)


class AuditSection(ImmutableModel):
    created_at: datetime
    created_by: str
    investigation_id: str
    workflow_id: str | None = None
    decision_version: str | None = None
    confidence_version: str | None = None
    source_services: tuple[str, ...] = ()
    provenance: tuple[ProvenanceReference, ...] = ()
    user_actions: tuple[dict[str, Any], ...] = ()
    execution_metadata: dict[str, Any] = Field(default_factory=dict)
    entries: tuple[AuditEntry, ...] = ()


class VersionMetadata(ImmutableModel):
    version: int
    version_id: UUID
    created_at: datetime
    created_by: str
    parent_version: int | None = None
    change_summary: str = 'initial case build'
    rollback_reference: int | None = None
    content_hash: str


class CaseStatistics(ImmutableModel):
    event_count: int = 0
    evidence_count: int = 0
    threat_count: int = 0
    hypothesis_count: int = 0
    recommendation_count: int = 0
    provenance_count: int = 0
    timeline_span_seconds: float = 0.0


class CaseRelationship(ImmutableModel):
    case_id: UUID
    related_case_id: UUID
    relationship: str
    created_at: datetime
    provenance: tuple[ProvenanceReference, ...] = ()


class CaseHistory(ImmutableModel):
    case_id: UUID
    versions: tuple[VersionMetadata, ...] = ()
    current_version: int = 1


class CaseSnapshot(ImmutableModel):
    case: 'CaseFile'
    captured_at: datetime
    reason: str


class CaseFile(ImmutableModel):
    case_id: UUID = Field(default_factory=uuid4)
    metadata: CaseMetadata
    executive_summary: ExecutiveSummary
    technical_summary: TechnicalSummary
    timeline: TimelineSection
    evidence: EvidenceSection
    threat: ThreatSection
    knowledge: KnowledgeSection
    graph: GraphSection
    historical: HistoricalSection
    hypotheses: HypothesisSection
    confidence: ConfidenceSection
    decision: DecisionSection
    recommendations: RecommendationSection
    execution: ExecutionSection
    references: ReferenceSection
    attachments: AttachmentSection
    audit: AuditSection
    version: VersionMetadata
    statistics: CaseStatistics
    relationships: tuple[CaseRelationship, ...] = ()
    context_metadata: dict[str, Any] = Field(default_factory=dict)


CaseSnapshot.model_rebuild()
