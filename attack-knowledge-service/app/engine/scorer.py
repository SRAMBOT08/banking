from __future__ import annotations
from typing import Dict, List, Tuple


def score_match(pattern: Dict, matched: List[str], missing: List[str]) -> Tuple[int, Dict]:
    """Deterministic scoring: required rules contribute weight, optional contribute lower weight."""
    score = 0
    breakdown = {}
    req_weight = pattern.get('weights', {}).get('required', 20)
    opt_weight = pattern.get('weights', {}).get('optional', 10)

    for r in pattern.get('required', []):
        contributed = req_weight if r in matched else 0
        breakdown[r] = contributed
        score += contributed

    for r in pattern.get('optional', []):
        contributed = opt_weight if r in matched else 0
        breakdown[r] = contributed
        score += contributed

    # clamp to 0-100
    if score > 100:
        score = 100
    return score, breakdown
