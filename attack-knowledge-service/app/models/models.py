from __future__ import annotations
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from uuid import uuid4


class InvestigationCandidate(BaseModel):
    candidate_id: str
    investigation_id: Optional[str]
    tenant_id: str
    correlation_id: Optional[str]
    pattern: str
    confidence: int
    explanation: Dict[str, Any]
    evidence_refs: List[Dict[str, Any]]
    version: str = "1.0"

    @classmethod
    def make(cls, tenant_id: str, correlation_id: str, pattern: str, confidence: int, explanation: Dict, evidence_refs: List[Dict], investigation_id: str = None):
        return cls(candidate_id=str(uuid4()), investigation_id=investigation_id, tenant_id=tenant_id, correlation_id=correlation_id, pattern=pattern, confidence=confidence, explanation=explanation, evidence_refs=evidence_refs)
