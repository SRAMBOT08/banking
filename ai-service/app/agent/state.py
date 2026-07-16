from __future__ import annotations
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class InvestigationState(BaseModel):
    investigation_id: str
    tenant_id: str
    status: str = Field(default="initialized")
    current_step: Optional[str] = None
    evidence: List[Dict[str, Any]] = Field(default_factory=list)
    evidence_graph: Dict[str, Any] = Field(default_factory=dict)
    candidate_patterns: List[Dict[str, Any]] = Field(default_factory=list)
    matched_patterns: List[Dict[str, Any]] = Field(default_factory=list)
    hypotheses: List[Dict[str, Any]] = Field(default_factory=list)
    selected_hypothesis: Optional[Dict[str, Any]] = None
    confidence: Optional[float] = None
    missing_evidence: List[Dict[str, Any]] = Field(default_factory=list)
    graph_results: Dict[str, Any] = Field(default_factory=dict)
    recommendations: List[Dict[str, Any]] = Field(default_factory=list)
    execution_plan: Dict[str, Any] = Field(default_factory=dict)
    ai_summary: Optional[str] = None
    history: List[Dict[str, Any]] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    def touch(self) -> None:
        """Update last modified timestamp."""
        self.updated_at = datetime.utcnow()

    def add_history(self, entry: Dict[str, Any]) -> None:
        self.history.append(entry)
        self.touch()
