from __future__ import annotations
from typing import Dict, List
from app.core.logger import get_logger
import hashlib

logger = get_logger("kr_validator")


def compute_checksum(obj: dict) -> str:
    import json

    s = json.dumps(obj, sort_keys=True)
    return hashlib.sha256(s.encode()).hexdigest()


def validate_patterns_basic(patterns: Dict[str, dict]) -> List[str]:
    errors = []
    seen_ids = set()
    for name, p in patterns.items():
        pid = p.get('name') or name
        version = p.get('version')
        if not pid:
            errors.append(f"pattern_missing_name_for_file:{name}")
        if not version:
            errors.append(f"pattern_missing_version:{pid}")
        key = f"{pid}:{version}"
        if key in seen_ids:
            errors.append(f"duplicate_pattern_version:{key}")
        seen_ids.add(key)
    return errors


def validate_pattern_references(patterns: Dict[str, dict]) -> List[str]:
    """Validate that pattern references such as related_patterns or depends_on exist and detect circular dependencies."""
    errors = []
    # build adjacency for depends_on / related_patterns
    adj = {}
    for name, p in patterns.items():
        pname = p.get('name') or name
        deps = p.get('depends_on') or p.get('related_patterns') or []
        adj[pname] = deps

    # detect missing references
    for n, deps in adj.items():
        for d in deps:
            if d not in adj:
                errors.append(f"missing_pattern_reference:{n}->{d}")

    # detect cycles using DFS
    visited = {}

    def dfs(node):
        if node not in adj:
            return False
        if visited.get(node) == 1:
            return True
        if visited.get(node) == 2:
            return False
        visited[node] = 1
        for nbr in adj.get(node, []):
            if dfs(nbr):
                return True
        visited[node] = 2
        return False

    for n in adj:
        if dfs(n):
            errors.append(f"circular_dependency_detected_starting_at:{n}")
            break

    return errors
