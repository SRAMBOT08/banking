from __future__ import annotations
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ReasonRequest(BaseModel):
    snapshot: Optional[Dict[str, Any]] = None
    investigation_id: Optional[str] = None
    snapshot_version: Optional[int] = None
    reasoning_type: str = "incident_summary"


class ChatRequest(ReasonRequest):
    message: str


class ReportRequest(ReasonRequest):
    report_type: str = "executive"
    format: str = "json"


class Claim(BaseModel):
    text: str
    source_ids: List[str] = Field(default_factory=list)


class AIResponse(BaseModel):
    reasoning_type: str
    snapshot_id: str
    snapshot_version: int
    answer: str
    claims: List[Claim] = Field(default_factory=list)
    recommendations: List[Dict[str, Any]] = Field(default_factory=list)
    confidence: int
    priority: str
    model: str
    usage: Dict[str, Any] = Field(default_factory=dict)
    latency_ms: float = 0.0


class ReportResponse(BaseModel):
    report_type: str
    format: str
    snapshot_id: str
    snapshot_version: int
    title: str
    sections: Dict[str, Any]
    traceability: List[str] = Field(default_factory=list)
    model: str
