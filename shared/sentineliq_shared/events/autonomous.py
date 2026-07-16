from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field


class EventIdentity(BaseModel):
    """Identity carried across every autonomous workflow boundary."""

    model_config = ConfigDict(extra="forbid")

    event_id: UUID = Field(default_factory=uuid4)
    event_version: str = "1.0"
    schema_version: str = "1.0"
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    tenant_id: str
    correlation_id: Optional[str] = None
    investigation_id: Optional[str] = None
    workflow_id: Optional[str] = None
    trace_id: Optional[str] = None
    source_id: str
    producer_service: str
    idempotency_key: str


class EvidenceGraphEvent(EventIdentity):
    event_type: str = "EVIDENCE_GRAPH_READY"
    source_event_ids: List[str] = Field(default_factory=list)
    evidence_graph: Dict[str, Any] = Field(default_factory=dict)


class CandidateEvent(EventIdentity):
    event_type: str = "INVESTIGATION_CANDIDATE"
    candidate_id: str
    pattern_name: str
    pattern_version: str = "1.0"
    confidence: float = 0.0
    matched_indicators: List[str] = Field(default_factory=list)
    missing_indicators: List[str] = Field(default_factory=list)
    evidence_refs: List[str] = Field(default_factory=list)
    recommendation: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class InvestigationCompletedEvent(EventIdentity):
    event_type: str = "INVESTIGATION_COMPLETED"
    decision: Optional[str] = None
    confidence: Optional[float] = None
    context: Dict[str, Any] = Field(default_factory=dict)
    snapshot: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class CaseCreatedEvent(EventIdentity):
    event_type: str = "CASE_CREATED"
    case_id: str
    case_version: int = 1
    case_file: Dict[str, Any] = Field(default_factory=dict)


class ReportGeneratedEvent(EventIdentity):
    event_type: str = "REPORT_GENERATED"
    report_id: str
    case_id: str
    case_version: int = 1
    report_type: str = "investigation"
    report_format: str = "json"
    report: Dict[str, Any] = Field(default_factory=dict)
    case_file: Dict[str, Any] = Field(default_factory=dict)
    source_hash: Optional[str] = None


class ExecutionCompletedEvent(EventIdentity):
    event_type: str = "EXECUTION_COMPLETED"
    execution_id: str
    status: str
    result: Dict[str, Any] = Field(default_factory=dict)
    error: Optional[str] = None


__all__ = [
    "EventIdentity",
    "EvidenceGraphEvent",
    "CandidateEvent",
    "InvestigationCompletedEvent",
    "CaseCreatedEvent",
    "ReportGeneratedEvent",
    "ExecutionCompletedEvent",
]
