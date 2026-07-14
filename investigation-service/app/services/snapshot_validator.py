from __future__ import annotations

from typing import List

from app.models.snapshot import InvestigationSnapshot


class SnapshotValidationError(ValueError):
    def __init__(self, findings: List[str]):
        self.findings = findings
        super().__init__("invalid investigation snapshot: " + ", ".join(findings))


class SnapshotValidator:
    def validate(self, snapshot: InvestigationSnapshot) -> List[str]:
        findings: List[str] = []
        item = snapshot.investigation
        if snapshot.metadata.investigation_id != item.investigation_id:
            findings.append("metadata_investigation_mismatch")
        if snapshot.summary.investigation_id != item.investigation_id:
            findings.append("summary_investigation_mismatch")
        if snapshot.summary.snapshot_version != snapshot.metadata.snapshot_version:
            findings.append("summary_version_mismatch")
        if [event.event_id for event in snapshot.timeline] != [event.event_id for event in item.timeline.events]:
            findings.append("timeline_integrity")
        if [evidence.evidence_id for evidence in snapshot.evidence] != [evidence.evidence_id for evidence in item.evidence]:
            findings.append("evidence_integrity")
        if snapshot.confidence != item.confidence:
            findings.append("confidence_consistency")
        if snapshot.confidence_history != [entry.model_dump() for entry in item.confidence_history]:
            findings.append("confidence_history_consistency")
        if [h.hypothesis_id for h in snapshot.hypotheses] != [h.hypothesis_id for h in item.hypotheses]:
            findings.append("hypothesis_consistency")
        if [r.recommendation_id for r in snapshot.recommendations] != [r.recommendation_id for r in item.investigation_plan]:
            findings.append("recommendation_consistency")
        if [m.evidence_type for m in snapshot.missing_evidence] != [m.evidence_type for m in item.missing_evidence]:
            findings.append("missing_evidence_consistency")
        if snapshot.metadata_context != item.metadata.model_dump():
            findings.append("metadata_consistency")
        if [event.sequence for event in snapshot.memory] != list(range(1, len(snapshot.memory) + 1)):
            findings.append("memory_sequence_integrity")
        if any(event.investigation_id != item.investigation_id for event in snapshot.memory):
            findings.append("memory_investigation_integrity")
        nodes = {node.get("id") for node in snapshot.graph.get("nodes", [])}
        if any(edge.get("from") not in nodes or edge.get("to") not in nodes for edge in snapshot.graph.get("edges", [])):
            findings.append("graph_integrity")
        return findings

    def assert_valid(self, snapshot: InvestigationSnapshot) -> InvestigationSnapshot:
        findings = self.validate(snapshot)
        if findings:
            raise SnapshotValidationError(findings)
        return snapshot
