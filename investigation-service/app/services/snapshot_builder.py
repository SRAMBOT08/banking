from __future__ import annotations

from copy import deepcopy
from typing import Iterable, Optional

from app.engine.graph import build_investigation_graph
from app.models.investigation import (Investigation, InvestigationEvidence as PydanticInvestigationEvidence,
                                      EvidenceSummary as PydanticEvidenceSummary,
                                      InvestigationRecommendation as PydanticInvestigationRecommendation)
from app.models.snapshot import InvestigationSnapshot, SnapshotMetadata, SnapshotSummary
from app.services.memory import InvestigationMemory


class SnapshotBuilder:
    """Builds a complete detached snapshot without mutating the live investigation."""

    def __init__(self, memory: InvestigationMemory):
        self.memory = memory

    @staticmethod
    def _is_wrapper_evidence(ev) -> bool:
        """Check if evidence is the deprecated wrapper class."""
        return type(ev).__module__ == 'app.services.investigation_manager' and type(ev).__name__ == 'InvestigationEvidence'

    @staticmethod
    def _is_wrapper_recommendation(rec) -> bool:
        """Check if recommendation is the deprecated wrapper class."""
        return type(rec).__module__ == 'app.services.investigation_manager' and type(rec).__name__ == 'InvestigationRecommendation'

    @staticmethod
    def _convert_evidence(evidence_list):
        """Convert deprecated wrapper objects to Pydantic models for snapshot."""
        if not evidence_list:
            return []
        converted = []
        for ev in evidence_list:
            if SnapshotBuilder._is_wrapper_evidence(ev):
                # Convert wrapper to Pydantic model
                converted.append(PydanticInvestigationEvidence(
                    evidence_id=ev.evidence_id,
                    evidence_type=ev.evidence_type,
                    timestamp=ev.timestamp,
                    confidence=ev.confidence,
                    properties=ev.properties,
                    source=ev.source
                ))
            else:
                # Already a Pydantic model or compatible
                converted.append(ev)
        return converted

    @staticmethod
    def _convert_evidence_summary(summary):
        """Convert deprecated wrapper to Pydantic model."""
        if summary is None:
            return PydanticEvidenceSummary()
        # Check if it's the wrapper class
        if type(summary).__module__ == 'app.services.investigation_manager' and type(summary).__name__ == 'EvidenceSummary':
            return PydanticEvidenceSummary(
                total=summary.total,
                by_type=summary.by_type,
                average_confidence=summary.average_confidence,
                evidence_ids=summary.evidence_ids
            )
        return summary

    @staticmethod
    def _convert_recommendations(rec_list):
        """Convert deprecated wrapper objects to Pydantic models."""
        if not rec_list:
            return []
        converted = []
        for rec in rec_list:
            if SnapshotBuilder._is_wrapper_recommendation(rec):
                converted.append(PydanticInvestigationRecommendation(
                    recommendation_id=rec.recommendation_id,
                    title=rec.title,
                    required_evidence=rec.required_evidence,
                    priority=rec.priority,
                    source_pattern=rec.source_pattern
                ))
            else:
                converted.append(rec)
        return converted

    def build(self, investigation: Investigation, metadata: SnapshotMetadata,
              related_investigations: Optional[Iterable[Investigation]] = None) -> InvestigationSnapshot:
        item = deepcopy(investigation)
        memory = self.memory.list(item.investigation_id)
        graph = build_investigation_graph(item)
        related_ids = sorted(other.investigation_id for other in (related_investigations or []))
        summary = SnapshotSummary(
            investigation_id=item.investigation_id,
            snapshot_id=metadata.snapshot_id,
            snapshot_version=metadata.snapshot_version,
            state=item.state,
            priority=item.priority,
            confidence=item.confidence.score,
            evidence_count=len(item.evidence),
            timeline_count=len(item.timeline.events),
            hypothesis_count=len(item.hypotheses),
            recommendation_count=len(item.investigation_plan),
            missing_evidence_count=len(item.missing_evidence),
            memory_event_count=len(memory),
            created_at=metadata.created_at,
            reason=metadata.reason,
        )
        return InvestigationSnapshot(
            metadata=metadata,
            investigation=item,
            timeline=deepcopy(item.timeline.events),
            evidence=self._convert_evidence(item.evidence),
            hypotheses=deepcopy(item.hypotheses),
            confidence=deepcopy(item.confidence),
            confidence_history=[entry.model_dump() for entry in item.confidence_history],
            recommendations=self._convert_recommendations(item.investigation_plan),
            missing_evidence=deepcopy(item.missing_evidence),
            related_entities=list(item.related_entities),
            related_investigations=related_ids,
            graph=deepcopy(graph),
            memory=deepcopy(memory),
            metadata_context=deepcopy(item.metadata.model_dump()),
            summary=summary,
        )
