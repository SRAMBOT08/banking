from __future__ import annotations
from typing import Dict, Any, List


def explain_match(pattern_name: str, matched: List[str], missing: List[str], breakdown: Dict, score: int, matched_edges: List[tuple]) -> Dict[str, Any]:
    return {
        "pattern": pattern_name,
        "matched": matched,
        "missing": missing,
        "score_breakdown": breakdown,
        "score": score,
        "matched_edges": matched_edges,
    }
