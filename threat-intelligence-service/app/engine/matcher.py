from __future__ import annotations

from typing import Any, Dict, List, Tuple

from app.knowledge_registry.manager import RegistryManager


def match_pattern_graph(registry: RegistryManager, pattern_name: str,
                        evidence_graph: Dict[str, Any]) -> Tuple[List[str], List[str], List[Tuple[str, str]]]:
    """Match one named pattern using only the RegistryManager public API."""
    pattern = registry.get_latest_pattern(pattern_name)
    if pattern is None:
        return [], [], []

    properties = [node.get("properties", {}) for node in evidence_graph.get("nodes", [])]

    def has_property(key: str, value: Any = None) -> bool:
        return any(key in item and (value is None or str(value) in str(item.get(key))) for item in properties)

    matched: List[str] = []
    missing: List[str] = []
    satisfied_nodes = set()
    for node in pattern.nodes:
        node_id = str(node.get("id") or node.get("name"))
        requirements = node.get("requires", [])
        if all(has_property(str(requirement)) for requirement in requirements):
            satisfied_nodes.add(node_id)
        for requirement in requirements:
            (matched if has_property(str(requirement)) else missing).append(str(requirement))

    matched_edges = [
        (str(edge.get("from")), str(edge.get("to")))
        for edge in pattern.edges
        if str(edge.get("from")) in satisfied_nodes and str(edge.get("to")) in satisfied_nodes
    ]
    return sorted(set(matched)), sorted(set(missing)), matched_edges
