from __future__ import annotations
from typing import Any, Dict, List
from app.models.context import AIContext


class RecommendationGenerator:
    """Returns only recommendations already present in the immutable snapshot."""
    def generate(self, context: AIContext) -> Dict[str, List[Dict[str, Any]]]:
        existing = [dict(item) for item in context.recommendations]
        missing = [dict(item) for item in context.missing_evidence]
        return {
            "immediate_actions": existing,
            "short_term_actions": existing,
            "long_term_actions": existing,
            "containment": existing,
            "recovery": existing,
            "monitoring": existing,
            "compliance_actions": existing,
            "risk_reduction": existing,
            "blocked_by_missing_evidence": missing,
        }
