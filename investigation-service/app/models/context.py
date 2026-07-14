from __future__ import annotations
from typing import Any, Dict, List
from pydantic import BaseModel, Field
from app.models.investigation import (Investigation, InvestigationEvidence, TimelineEvent, Hypothesis,
                                      InvestigationConfidence, MissingEvidence, InvestigationRecommendation)
from app.models.memory import InvestigationMemoryEvent


class InvestigationContext(BaseModel):
    investigation: Investigation
    timeline: List[TimelineEvent] = Field(default_factory=list)
    evidence: List[InvestigationEvidence] = Field(default_factory=list)
    hypotheses: List[Hypothesis] = Field(default_factory=list)
    pattern_matches: List[Dict[str, Any]] = Field(default_factory=list)
    confidence: InvestigationConfidence
    confidence_history: List[Dict[str, Any]] = Field(default_factory=list)
    missing_evidence: List[MissingEvidence] = Field(default_factory=list)
    recommendations: List[InvestigationRecommendation] = Field(default_factory=list)
    investigation_graph: Dict[str, Any] = Field(default_factory=dict)
    related_entities: List[str] = Field(default_factory=list)
    related_investigations: List[str] = Field(default_factory=list)
    memory: List[InvestigationMemoryEvent] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
