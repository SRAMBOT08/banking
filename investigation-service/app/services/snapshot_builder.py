from __future__ import annotations

from copy import deepcopy
from typing import Iterable, Optional

from app.engine.graph import build_investigation_graph
from app.models.investigation import Investigation
from app.models.snapshot import InvestigationSnapshot, SnapshotMetadata, SnapshotSummary
from app.services.memory import InvestigationMemory


class SnapshotBuilder:
    """Builds a complete detached snapshot without mutating the live investigation."""

    def __init__(self, memory: InvestigationMemory):
        self.memory = memory

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
            evidence=deepcopy(item.evidence),
            hypotheses=deepcopy(item.hypotheses),
            confidence=deepcopy(item.confidence),
            confidence_history=[entry.model_dump() for entry in item.confidence_history],
            recommendations=deepcopy(item.investigation_plan),
            missing_evidence=deepcopy(item.missing_evidence),
            related_entities=list(item.related_entities),
            related_investigations=related_ids,
            graph=deepcopy(graph),
            memory=deepcopy(memory),
            metadata_context=deepcopy(item.metadata.model_dump()),
            summary=summary,
        )
