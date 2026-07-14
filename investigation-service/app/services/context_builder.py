from __future__ import annotations
from app.engine.graph import build_investigation_graph
from app.models.context import InvestigationContext
from app.models.investigation import Investigation
from app.services.memory import InvestigationMemory


class InvestigationContextBuilder:
    """Pure aggregation boundary for the future AI Investigation Service."""
    def __init__(self, memory: InvestigationMemory):
        self.memory = memory

    def build(self, investigation: Investigation, related_investigations=None) -> InvestigationContext:
        related_ids = sorted(item.investigation_id for item in (related_investigations or []))
        return InvestigationContext(
            investigation=investigation,
            timeline=list(investigation.timeline.events),
            evidence=list(investigation.evidence),
            hypotheses=list(investigation.hypotheses),
            pattern_matches=[hypothesis.model_dump() for hypothesis in investigation.hypotheses],
            confidence=investigation.confidence,
            confidence_history=[item.model_dump() for item in investigation.confidence_history],
            missing_evidence=list(investigation.missing_evidence),
            recommendations=list(investigation.investigation_plan),
            investigation_graph=build_investigation_graph(investigation),
            related_entities=list(investigation.related_entities),
            related_investigations=related_ids,
            memory=self.memory.list(investigation.investigation_id),
            metadata=investigation.metadata.model_dump(),
        )
