from __future__ import annotations
from typing import Dict, List


def explain_candidate(pattern_name: str, pattern: Dict, matched: List[str], missing: List[str], breakdown: Dict, score: int, evidence_refs: List[Dict]) -> Dict:
    return {
        "pattern": pattern_name,
        "matched_rules": matched,
        "missing_rules": missing,
        "score_breakdown": breakdown,
        "score": score,
        "evidence_references": evidence_refs,
    }
