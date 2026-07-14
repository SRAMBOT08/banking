from __future__ import annotations
from typing import Dict, List, Tuple


def match_pattern(pattern: Dict, evidence_graph: Dict) -> Tuple[List[str], List[str]]:
    """Return (matched_rules, missing_rules) based on pattern requirements/optional and evidence nodes."""
    matched = []
    missing = []

    # evidence nodes keys: list of node types or properties
    nodes = evidence_graph.get('nodes', [])
    props = []
    for n in nodes:
        props.append(n.get('properties', {}))

    def has_property(key, value=None):
        for p in props:
            if key in p:
                if value is None or p.get(key) == value or str(value) in str(p.get(key)):
                    return True
        return False

    # required rules
    for r in pattern.get('required', []):
        if has_property(r):
            matched.append(r)
        else:
            missing.append(r)

    # optional rules
    for r in pattern.get('optional', []):
        if has_property(r):
            matched.append(r)

    return matched, missing
