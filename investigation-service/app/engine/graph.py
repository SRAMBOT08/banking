from __future__ import annotations
from typing import Any, Dict, List, Optional
from app.models.investigation import Investigation


def build_investigation_graph(investigation: Investigation) -> Dict[str, List[Dict[str, Any]]]:
    nodes = [{"id": investigation.investigation_id, "type": "investigation", "label": investigation.investigation_id}]
    edges = []

    def add(node_id, node_type, label, relation):
        nodes.append({"id": node_id, "type": node_type, "label": label})
        edges.append({"from": investigation.investigation_id, "to": node_id, "type": relation})

    for hypothesis in investigation.hypotheses:
        add(hypothesis.hypothesis_id, "hypothesis", hypothesis.pattern_name, "HAS_HYPOTHESIS")
    for evidence in investigation.evidence:
        add(evidence.evidence_id, "evidence", evidence.evidence_type, "HAS_EVIDENCE")
    for event in investigation.timeline.events:
        add(event.event_id, "timeline", event.event_type, "HAS_TIMELINE_EVENT")
    for recommendation in investigation.investigation_plan:
        add(recommendation.recommendation_id, "recommendation", recommendation.title, "HAS_RECOMMENDATION")
    for missing in investigation.missing_evidence:
        add(f"missing:{missing.evidence_type}", "missing_evidence", missing.evidence_type, "MISSING_EVIDENCE")
    add("priority", "priority", investigation.priority.value, "HAS_PRIORITY")
    add("confidence", "confidence", str(investigation.confidence.score), "HAS_CONFIDENCE")
    return {"nodes": nodes, "edges": edges}


def find_relationships(graph: Dict[str, List[Dict[str, Any]]], node_id: str, relationship: Optional[str] = None):
    return [edge for edge in graph.get("edges", []) if (edge["from"] == node_id or edge["to"] == node_id) and (relationship is None or edge["type"] == relationship)]


def find_related(graph: Dict[str, List[Dict[str, Any]]], node_id: str):
    related = {edge["to"] if edge["from"] == node_id else edge["from"] for edge in find_relationships(graph, node_id)}
    return [node for node in graph.get("nodes", []) if node["id"] in related]
