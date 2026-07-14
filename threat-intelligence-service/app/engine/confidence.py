from __future__ import annotations

from typing import Any, Dict, List, Tuple


def propagate_confidence(pattern: Any, matched: List[str], missing: List[str]) -> Tuple[int, Dict[str, int]]:
    """Compute a deterministic 0-100 score from typed pattern evidence."""
    data = pattern.model_dump() if hasattr(pattern, "model_dump") else pattern
    model = data.get("confidence_model") or {}
    weights = model if model else data.get("weights", {})
    required = weights.get("required", 25)
    optional = weights.get("optional", 10)
    if not isinstance(required, dict):
        required = {str(req): required for node in data.get("nodes", []) for req in node.get("requires", [])}
    if not isinstance(optional, dict):
        optional = {str(req): optional for req in data.get("optional", [])}
    matched_set = set(matched)
    breakdown: Dict[str, int] = {}
    score = 0
    for requirement, weight in sorted(required.items()):
        contribution = int(weight) if requirement in matched_set else 0
        breakdown[requirement] = contribution
        score += contribution
    for requirement, weight in sorted(optional.items()):
        contribution = int(weight) if requirement in matched_set else 0
        breakdown[requirement] = contribution
        score += contribution
    return min(100, score), breakdown
