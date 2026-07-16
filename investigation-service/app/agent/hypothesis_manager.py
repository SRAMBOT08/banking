from __future__ import annotations
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, List, Optional
from uuid import uuid4


class HypothesisManager:
    def create(self, name: str, description: str, supporting_evidence: Optional[List[Dict[str, Any]]] = None, priority: int = 0, relationships: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        return {"id": f"hyp-{uuid4().hex}", "name": name, "description": description, "supporting_evidence": supporting_evidence or [], "missing_evidence": [], "confidence": 0.0, "priority": priority, "status": "active", "reasoning_history": [], "relationships": relationships or [], "created_at": datetime.now(timezone.utc).isoformat()}

    def generate(self, patterns: Iterable[Dict[str, Any]]) -> List[Dict[str, Any]]:
        return [self.create(p.get("name", p.get("id", "pattern")), p.get("description", ""), p.get("evidence", []), int(p.get("priority", 0))) for p in patterns]

    def create(self, name: str, description: str, supporting_evidence: Optional[List[Dict[str, Any]]] = None, priority: int = 0, relationships: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        return {"id": f"hyp-{uuid4().hex}", "name": name, "description": description, "supporting_evidence": supporting_evidence or [], "missing_evidence": [], "confidence": 0.0, "priority": priority, "status": "active", "reasoning_history": [], "relationships": relationships or [], "created_at": datetime.now(timezone.utc).isoformat()}

    def update(self, hypothesis: Dict[str, Any], **changes: Any) -> Dict[str, Any]:
        updated = {**hypothesis, **changes}
        updated.setdefault("reasoning_history", []).append({"event": "updated", "changes": changes, "timestamp": datetime.now(timezone.utc).isoformat()})
        return updated

    def reject(self, hypothesis: Dict[str, Any], reason: str) -> Dict[str, Any]:
        return self.update(hypothesis, status="rejected", rejection_reason=reason)

    def close(self, hypothesis: Dict[str, Any], reason: str = "") -> Dict[str, Any]:
        return self.update(hypothesis, status="closed", closure_reason=reason)

    def archive(self, hypothesis: Dict[str, Any]) -> Dict[str, Any]:
        return self.update(hypothesis, status="archived")

    def restore(self, hypothesis: Dict[str, Any]) -> Dict[str, Any]:
        return self.update(hypothesis, status="active")

    def merge(self, primary: Dict[str, Any], secondary: Dict[str, Any]) -> Dict[str, Any]:
        merged = self.update(primary, supporting_evidence=primary.get("supporting_evidence", []) + secondary.get("supporting_evidence", []), missing_evidence=primary.get("missing_evidence", []) + secondary.get("missing_evidence", []), relationships=primary.get("relationships", []) + [{"type": "merged", "hypothesis_id": secondary.get("id")}])
        return merged

    def rank(self, hypotheses: Iterable[Dict[str, Any]]) -> List[Dict[str, Any]]:
        return sorted(hypotheses, key=lambda h: (h.get("status") == "active", float(h.get("confidence", 0)), int(h.get("priority", 0))), reverse=True)
