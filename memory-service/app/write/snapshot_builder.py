from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Mapping

from ..query.models import (
    HistoricalEvidence, HistoricalGraph, HistoricalKnowledge, HistoricalThreat,
    InvestigationConfidence, InvestigationDecision, InvestigationHypothesis,
    InvestigationMetadata, InvestigationOutcome, InvestigationSnapshot,
    InvestigationSummary, InvestigationTimeline, InvestigationTimelineEvent,
    LessonsLearned, Severity, CaseStatus, OutcomeType,
)


class IncompleteInvestigationError(ValueError):
    """Raised when a non-completed investigation is submitted for memory."""


class InvestigationSnapshotBuilder:
    """Builds durable case intelligence while excluding raw operational data."""

    def build(self, completed_investigation: Mapping[str, Any]) -> InvestigationSnapshot:
        status = str(completed_investigation.get("workflow_status", "")).casefold()
        if status not in {"completed", "closed", "reviewed"}:
            raise IncompleteInvestigationError("only completed investigations can be stored in memory")

        investigation_id = str(completed_investigation["investigation_id"])
        tenant_id = str(completed_investigation["tenant_id"])
        now = datetime.now(timezone.utc)
        metadata = completed_investigation.get("metadata", {})
        evidence = completed_investigation.get("evidence", [])
        patterns = completed_investigation.get("matched_patterns", []) or completed_investigation.get("candidate_patterns", [])
        knowledge = completed_investigation.get("knowledge", {})
        graph = completed_investigation.get("graph_results", {})
        confidence = completed_investigation.get("confidence_breakdown", {})
        final_confidence = float(completed_investigation.get("final_confidence") or confidence.get("overall", 0.0) or 0.0)
        created_at = completed_investigation.get("created_at", now)
        completed_at = completed_investigation.get("updated_at", now)
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
        if isinstance(completed_at, str):
            completed_at = datetime.fromisoformat(completed_at.replace("Z", "+00:00"))

        summary = InvestigationSummary(
            investigation_id=investigation_id,
            title=str(metadata.get("title", f"Investigation {investigation_id}")),
            summary=str(metadata.get("summary", "Completed investigation snapshot")),
            severity=Severity(str(metadata.get("severity", "medium")).casefold()),
            case_status=CaseStatus.COMPLETED,
            fraud_category=metadata.get("fraud_category"),
            root_cause=metadata.get("root_cause"),
            final_confidence=max(0.0, min(1.0, final_confidence)),
            mitre_mapping=list(metadata.get("mitre_mapping", [])),
            tags=list(metadata.get("tags", [])),
        )
        historical_evidence = [HistoricalEvidence(evidence_id=str(item.get("evidence_id", item.get("id", ""))), evidence_type=str(item.get("evidence_type", item.get("type", "unknown"))), source=item.get("source"), risk_score=item.get("risk_score")) for item in evidence if item.get("evidence_id", item.get("id"))]
        historical_threat = [HistoricalThreat(threat_id=str(item.get("threat_id", item.get("id", ""))), pattern_name=str(item.get("pattern_name", item.get("name", "unknown"))), confidence=float(item.get("confidence", 0.0)), references=list(item.get("evidence_refs", []))) for item in patterns if item.get("threat_id", item.get("id"))]
        knowledge_items = knowledge.get("items", []) if isinstance(knowledge, Mapping) else []
        historical_knowledge = [HistoricalKnowledge(knowledge_id=str(item.get("id")), category=item.get("category"), version=item.get("version")) for item in knowledge_items if item.get("id")]
        graph_nodes = graph.get("nodes", []) if isinstance(graph, Mapping) else []
        historical_graph = [HistoricalGraph(node_ids=[str(item.get("id")) for item in graph_nodes if item.get("id")], relationship_ids=[str(item.get("id")) for item in graph.get("relationships", []) if item.get("id")], community_id=graph.get("community_id"), centrality_score=graph.get("centrality"))] if graph_nodes or graph.get("relationships") else []
        timeline = InvestigationTimeline(investigation_id=investigation_id, events=[InvestigationTimelineEvent(event_id=f"{investigation_id}:completed", event_type="investigation_completed", timestamp=completed_at, description="Investigation completed", entity_id=metadata.get("entity_id"))])
        return InvestigationSnapshot(summary=summary, metadata=InvestigationMetadata(tenant_id=tenant_id, analyst_id=metadata.get("analyst_id"), created_at=created_at, completed_at=completed_at, duration_seconds=max(0.0, (completed_at - created_at).total_seconds()), severity=summary.severity, case_status=CaseStatus.COMPLETED, workflow_id=metadata.get("workflow_id")), evidence_references=historical_evidence, threat_references=historical_threat, knowledge_references=historical_knowledge, graph_references=historical_graph, hypotheses=[InvestigationHypothesis.model_validate(item) for item in completed_investigation.get("hypotheses", []) if item.get("hypothesis_id")], confidence=InvestigationConfidence(overall=final_confidence, evidence=float(confidence.get("evidence", 0.0)), threat=float(confidence.get("threat", 0.0)), knowledge=float(confidence.get("knowledge", 0.0)), graph=float(confidence.get("graph", 0.0)), historical=float(confidence.get("historical", 0.0))), decision=InvestigationDecision.model_validate(completed_investigation["decision"]) if completed_investigation.get("decision") else None, outcome=InvestigationOutcome(outcome_type=OutcomeType(str(metadata.get("outcome_type", "undetermined")).casefold()), success=bool(metadata.get("outcome_success", False)), root_cause=metadata.get("root_cause"), resolution=metadata.get("resolution"), analyst_notes=str(metadata.get("analyst_notes", "")), completed_at=completed_at), resolution=metadata.get("resolution"), analyst_notes=str(metadata.get("analyst_notes", "")), lessons_learned=LessonsLearned(investigation_id=investigation_id, lessons=list(metadata.get("lessons_learned", [])), prevention_actions=list(metadata.get("prevention_actions", []))), related_investigation_ids=list(metadata.get("related_investigation_ids", [])), similarity_features={"risk_score": metadata.get("risk_score"), "entity_ids": list(metadata.get("entity_ids", []))}, timeline=timeline)
