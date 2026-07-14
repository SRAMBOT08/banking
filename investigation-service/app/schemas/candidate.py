from __future__ import annotations
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, ConfigDict


class CandidateInput(BaseModel):
    model_config = ConfigDict(extra="ignore")
    candidate_id: str
    investigation_id: Optional[str] = None
    correlation_id: Optional[str] = None
    tenant_id: str = "tenant-unknown"
    pattern_name: str
    pattern_version: str = "1.0"
    confidence: int = Field(ge=0, le=100)
    explanation: Dict[str, Any] = Field(default_factory=dict)
    evidence_refs: List[Any] = Field(default_factory=list)
    timestamp: str
    matched_indicators: List[str] = Field(default_factory=list)
    missing_indicators: List[str] = Field(default_factory=list)
    mitre_mapping: Optional[Any] = None
    fraud_mapping: Optional[Any] = None
    recommendation: Optional[Any] = None
