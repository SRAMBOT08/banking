from typing import Any, Dict, List
from pydantic import BaseModel, Field
from app.models.investigation import Investigation, InvestigationState, InvestigationRecommendation, MissingEvidence
from app.models.context import InvestigationContext
from app.models.memory import InvestigationMemoryEvent
from app.models.metrics import InvestigationMetrics


class InvestigationListResponse(BaseModel):
    investigations: List[Investigation] = Field(default_factory=list)


class TimelineResponse(BaseModel):
    investigation_id: str
    events: List[Any] = Field(default_factory=list)


class MemoryResponse(BaseModel):
    investigation_id: str
    events: List[InvestigationMemoryEvent] = Field(default_factory=list)


class GraphResponse(BaseModel):
    investigation_id: str
    graph: Dict[str, Any] = Field(default_factory=dict)


class ReplayResponse(BaseModel):
    investigation_id: str
    investigation: Investigation
    events: List[InvestigationMemoryEvent] = Field(default_factory=list)


class TransitionRequest(BaseModel):
    state: InvestigationState
    reason: str = "API transition"


class MetricsResponse(InvestigationMetrics):
    pass


class ContextResponse(InvestigationContext):
    pass


class HealthResponse(BaseModel):
    status: str
    service: str


class RecommendationsResponse(BaseModel):
    investigation_id: str
    recommendations: List[InvestigationRecommendation] = Field(default_factory=list)


class MissingEvidenceResponse(BaseModel):
    investigation_id: str
    missing_evidence: List[MissingEvidence] = Field(default_factory=list)
