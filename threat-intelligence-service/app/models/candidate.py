from __future__ import annotations
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from uuid import uuid4
from datetime import datetime


class InvestigationCandidate(BaseModel):
    candidate_id: str
    investigation_id: Optional[str]
    correlation_id: Optional[str]
    tenant_id: str
    pattern_name: str
    pattern_version: str
    confidence: int
    explanation: Dict[str, Any]
    evidence_refs: List[Dict[str, Any]]
    timestamp: str
    version: str = "1.0"

    @classmethod
    def create(cls, tenant_id: str, correlation_id: Optional[str], pattern_name: str, pattern_version: str, confidence: int, explanation: Dict[str, Any], evidence_refs: List[Dict[str, Any]], investigation_id: Optional[str] = None):
        return cls(candidate_id=str(uuid4()), investigation_id=investigation_id, correlation_id=correlation_id, tenant_id=tenant_id, pattern_name=pattern_name, pattern_version=pattern_version, confidence=confidence, explanation=explanation, evidence_refs=evidence_refs, timestamp=datetime.utcnow().isoformat() + "Z")
