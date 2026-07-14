from __future__ import annotations

import hashlib
import json
from typing import Any, Dict, Iterable, List

VALID_SEVERITIES = {"low", "medium", "high", "critical"}
VALID_RISK_LEVELS = {"low", "medium", "high", "critical"}


def compute_checksum(obj: dict) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True).encode()).hexdigest()


def _has_cycle(edges: Iterable[tuple[str, str]]) -> bool:
    graph: Dict[str, List[str]] = {}
    for source, target in edges:
        graph.setdefault(source, []).append(target)
        graph.setdefault(target, [])
    visiting, visited = set(), set()

    def visit(node: str) -> bool:
        if node in visiting:
            return True
        if node in visited:
            return False
        visiting.add(node)
        if any(visit(child) for child in graph[node]):
            return True
        visiting.remove(node)
        visited.add(node)
        return False

    return any(visit(node) for node in graph)


def validate_registry(patterns: Dict[str, dict]) -> List[Dict[str, Any]]:
    findings: List[Dict[str, Any]] = []
    pattern_keys = {(str(p.get("name") or key), str(p.get("version"))) for key, p in patterns.items()}
    recommendation_ids = set()
    recommendation_edges: List[tuple[str, str]] = []
    dependency_edges: List[tuple[str, str]] = []
    all_indicator_ids = set()
    for pattern in patterns.values():
        for item in pattern.get("indicators", []):
            identifier = item if isinstance(item, str) else item.get("id")
            if identifier:
                all_indicator_ids.add(str(identifier))

    def add(code: str, description: str, location: str, severity: str = "critical") -> None:
        findings.append({"code": code, "category": "registry", "severity": severity,
                         "description": description, "location": location,
                         "suggested_fix": "Correct the referenced knowledge document."})

    for key, pattern in sorted(patterns.items()):
        name = str(pattern.get("name") or key)
        version = pattern.get("version")
        if not pattern.get("name"):
            add("missing_pattern_name", "Pattern name is required", key)
        if not version:
            add("missing_pattern_version", "Pattern version is required", name)

        metadata = pattern.get("metadata") or {}
        for field, allowed in (("severity", VALID_SEVERITIES), ("risk_level", VALID_RISK_LEVELS)):
            value = pattern.get(field, metadata.get(field))
            if value is not None and str(value).casefold() not in allowed:
                add(f"invalid_{field}", f"Invalid {field}: {value}", f"{name}.{field}")

        node_ids = {str(node.get("id") or node.get("name")) for node in pattern.get("nodes", [])}
        for edge in pattern.get("edges", []):
            source, target = str(edge.get("from", "")), str(edge.get("to", ""))
            if source not in node_ids or target not in node_ids:
                add("orphan_relationship", f"Relationship references missing node: {source}->{target}", name)

        model = pattern.get("confidence_model")
        if model is not None:
            valid = isinstance(model, dict)
            weights = []
            if valid:
                for group in ("required", "optional"):
                    values = model.get(group, {})
                    valid = valid and isinstance(values, dict)
                    weights.extend(values.values() if isinstance(values, dict) else [])
                valid = valid and all(isinstance(value, int) and not isinstance(value, bool) and value >= 0 for value in weights)
                valid = valid and any(weights)
            if not valid:
                add("invalid_confidence_model", "Confidence weights must be non-negative integers with a positive total", name)

        mitre = pattern.get("mitre") or {}
        technique = mitre.get("technique") or mitre.get("id")
        if technique is not None and not str(technique).upper().startswith("T"):
            add("invalid_mitre_reference", f"Invalid MITRE technique: {technique}", name)

        indicator_references = pattern.get("indicator_refs", [])
        indicator_references += (pattern.get("fraud") or {}).get("indicators", [])
        for indicator in indicator_references:
            identifier = indicator if isinstance(indicator, str) else indicator.get("id")
            if identifier and str(identifier) not in all_indicator_ids:
                add("missing_indicator", f"Missing indicator: {identifier}", name)

        recommendations = pattern.get("recommendations", pattern.get("recommendation", [])) or []
        for recommendation in recommendations:
            recommendation_id = recommendation.get("id") if isinstance(recommendation, dict) else recommendation
            if not recommendation_id:
                add("missing_recommendation_id", "Recommendation id is required", name)
                continue
            if recommendation_id in recommendation_ids:
                add("duplicate_recommendation", f"Duplicate recommendation: {recommendation_id}", name)
            recommendation_ids.add(recommendation_id)
            if isinstance(recommendation, dict):
                for required in recommendation.get("required_evidence", []):
                    if str(required) not in node_ids and str(required) not in all_indicator_ids:
                        add("orphan_recommendation", f"Recommendation references missing evidence: {required}", name)
                recommendation_edges.extend((str(recommendation_id), str(target)) for target in recommendation.get("depends_on", []))

        dependencies = metadata.get("dependencies", []) + pattern.get("dependencies", [])
        for dependency in dependencies:
            dependency_edges.append((name, str(dependency)))
            if not any(existing_name == str(dependency) for existing_name, _ in pattern_keys):
                add("orphan_dependency", f"Missing dependency: {dependency}", name)

    if _has_cycle(dependency_edges):
        add("cyclic_dependency_graph", "Pattern dependencies contain a cycle", "dependencies")
    if _has_cycle(recommendation_edges):
        add("cyclic_recommendation_graph", "Recommendation dependencies contain a cycle", "recommendations")
    return findings


def validate_patterns_basic(patterns: Dict[str, dict]) -> List[str]:
    return [f"{finding['code']}:{finding['location']}" for finding in validate_registry(patterns)]


def validate_pattern_references(patterns: Dict[str, dict]) -> List[str]:
    return validate_patterns_basic(patterns)
