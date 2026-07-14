from pydantic import BaseModel, Field
from typing import Dict


class InvestigationMetrics(BaseModel):
    open_investigations: int = 0
    closed_investigations: int = 0
    average_investigation_time_seconds: float = 0.0
    average_confidence: float = 0.0
    evidence_count: int = 0
    pattern_distribution: Dict[str, int] = Field(default_factory=dict)
    priority_distribution: Dict[str, int] = Field(default_factory=dict)
    attack_type_distribution: Dict[str, int] = Field(default_factory=dict)
    state_distribution: Dict[str, int] = Field(default_factory=dict)
    missing_evidence_frequency: Dict[str, int] = Field(default_factory=dict)
    recommendation_frequency: Dict[str, int] = Field(default_factory=dict)
