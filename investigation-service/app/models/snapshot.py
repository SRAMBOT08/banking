from __future__ import annotations

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field

from app.models.context import InvestigationContext
from app.models.investigation import (
    Investigation,
    InvestigationConfidence,
    InvestigationEvidence,
    InvestigationPriority,
    InvestigationRecommendation,
    InvestigationState,
    MissingEvidence,
    Hypothesis,
    TimelineEvent,
)
from app.models.memory import InvestigationMemoryEvent


class SnapshotMetadata(BaseModel):
    model_config = ConfigDict(frozen=True)

    snapshot_id: str
    snapshot_version: int
    investigation_version: str
    investigation_id: str
    created_at: str
    created_by: str = "investigation-service"
    reason: str
    parent_snapshot: Optional[str] = None


class SnapshotVersion(BaseModel):
    model_config = ConfigDict(frozen=True)

    snapshot_id: str
    investigation_id: str
    version: int
    created_at: str
    parent_snapshot: Optional[str] = None


class SnapshotHistory(BaseModel):
    model_config = ConfigDict(frozen=True)

    investigation_id: str
    versions: List[SnapshotVersion] = Field(default_factory=list)


class SnapshotSummary(BaseModel):
    model_config = ConfigDict(frozen=True)

    investigation_id: str
    snapshot_id: str
    snapshot_version: int
    state: InvestigationState
    priority: InvestigationPriority
    confidence: int
    evidence_count: int
    timeline_count: int
    hypothesis_count: int
    recommendation_count: int
    missing_evidence_count: int
    memory_event_count: int
    created_at: str
    reason: str


class InvestigationSnapshot(BaseModel):
    """Immutable, complete point-in-time investigation state."""

    model_config = ConfigDict(frozen=True)

    metadata: SnapshotMetadata
    investigation: Investigation
    timeline: List[TimelineEvent] = Field(default_factory=list)
    evidence: List[InvestigationEvidence] = Field(default_factory=list)
    hypotheses: List[Hypothesis] = Field(default_factory=list)
    confidence: InvestigationConfidence
    confidence_history: List[Dict[str, Any]] = Field(default_factory=list)
    recommendations: List[InvestigationRecommendation] = Field(default_factory=list)
    missing_evidence: List[MissingEvidence] = Field(default_factory=list)
    related_entities: List[str] = Field(default_factory=list)
    related_investigations: List[str] = Field(default_factory=list)
    graph: Dict[str, Any] = Field(default_factory=dict)
    memory: List[InvestigationMemoryEvent] = Field(default_factory=list)
    metadata_context: Dict[str, Any] = Field(default_factory=dict)
    summary: SnapshotSummary


class SnapshotDiff(BaseModel):
    model_config = ConfigDict(frozen=True)

    investigation_id: str
    from_snapshot: int
    to_snapshot: int
    added_evidence: List[InvestigationEvidence] = Field(default_factory=list)
    removed_evidence: List[InvestigationEvidence] = Field(default_factory=list)
    confidence_changes: Dict[str, Any] = Field(default_factory=dict)
    timeline_added: List[TimelineEvent] = Field(default_factory=list)
    timeline_removed: List[TimelineEvent] = Field(default_factory=list)
    state_changes: Dict[str, str] = Field(default_factory=dict)
    recommendation_added: List[InvestigationRecommendation] = Field(default_factory=list)
    recommendation_removed: List[InvestigationRecommendation] = Field(default_factory=list)
    priority_changes: Dict[str, str] = Field(default_factory=dict)
    missing_evidence_added: List[MissingEvidence] = Field(default_factory=list)
    missing_evidence_removed: List[MissingEvidence] = Field(default_factory=list)


class SnapshotStatistics(BaseModel):
    snapshot_count: int = 0
    average_snapshot_size: float = 0.0
    average_snapshot_time_seconds: float = 0.0
    snapshots_per_investigation: Dict[str, int] = Field(default_factory=dict)
    latest_version: Dict[str, int] = Field(default_factory=dict)
    oldest_version: Dict[str, int] = Field(default_factory=dict)


class SnapshotMetadataEvent(BaseModel):
    event_id: str
    event_type: str = "INVESTIGATION_SNAPSHOT_CREATED"
    schema_version: str = "1.0"
    investigation_id: str
    snapshot_id: str
    snapshot_version: int
    timestamp: str
    tenant_id: str
    reason: str
    parent_snapshot: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
