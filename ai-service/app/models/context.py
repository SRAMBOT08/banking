from __future__ import annotations
from typing import Any, Dict, Tuple
from pydantic import BaseModel, ConfigDict, Field
from app.models.snapshot_contract import SnapshotDocument


class AIContext(BaseModel):
    """The only context shape accepted by the AI reasoning layer."""
    model_config = ConfigDict(frozen=True)
    snapshot_id: str
    snapshot_version: int
    investigation: Dict[str, Any]
    timeline: Tuple[Dict[str, Any], ...] = Field(default_factory=tuple)
    evidence: Tuple[Dict[str, Any], ...] = Field(default_factory=tuple)
    hypotheses: Tuple[Dict[str, Any], ...] = Field(default_factory=tuple)
    recommendations: Tuple[Dict[str, Any], ...] = Field(default_factory=tuple)
    priority: str
    confidence: Dict[str, Any]
    confidence_history: Tuple[Dict[str, Any], ...] = Field(default_factory=tuple)
    graph_summary: Dict[str, Any]
    related_investigations: Tuple[str, ...] = Field(default_factory=tuple)
    missing_evidence: Tuple[Dict[str, Any], ...] = Field(default_factory=tuple)
    metadata: Dict[str, Any]

    @classmethod
    def from_snapshot(cls, snapshot: SnapshotDocument) -> "AIContext":
        investigation = dict(snapshot.investigation)
        return cls(
            snapshot_id=str(snapshot.metadata["snapshot_id"]),
            snapshot_version=int(snapshot.metadata["snapshot_version"]),
            investigation=investigation,
            timeline=tuple(snapshot.timeline),
            evidence=tuple(snapshot.evidence),
            hypotheses=tuple(snapshot.hypotheses),
            recommendations=tuple(snapshot.recommendations),
            priority=str(investigation.get("priority", snapshot.summary.get("priority", "UNKNOWN"))),
            confidence=dict(snapshot.confidence),
            confidence_history=tuple(snapshot.confidence_history),
            graph_summary={
                "node_count": len(snapshot.graph.get("nodes", [])),
                "edge_count": len(snapshot.graph.get("edges", [])),
                "node_types": sorted({str(node.get("type", "unknown")) for node in snapshot.graph.get("nodes", [])}),
            },
            related_investigations=tuple(snapshot.related_investigations),
            missing_evidence=tuple(snapshot.missing_evidence),
            metadata=dict(snapshot.metadata_context or snapshot.metadata),
        )
