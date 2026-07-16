from __future__ import annotations
from typing import Any
from .correlation_engine import CorrelationEngine
from .models import ContextMetadata, EvidenceContext, GraphContext, HistoricalContext, InvestigationContext, KnowledgeContext, MergeStatistics, ThreatContext
from .validator import ContextValidator


class ContextBuilder:
    def build(self, *, state: Any, sections: dict[str, list[dict[str, Any]]], raw: dict[str, dict[str, Any]], provenance: list[Any], confidence: list[Any], merge_statistics: MergeStatistics, missing: list[str]) -> InvestigationContext:
        correlation_id = str(state.metadata.get("correlation_id") or state.investigation_id)
        context = InvestigationContext(
            metadata=ContextMetadata(investigation_id=state.investigation_id, tenant_id=state.tenant_id, workflow_id=state.metadata.get("workflow_id"), correlation_id=correlation_id, services_queried=sorted(raw)),
            evidence_context=EvidenceContext(items=sections.get("evidence", []), raw=raw.get("evidence", {}), result_count=len(sections.get("evidence", []))),
            threat_context=ThreatContext(items=sections.get("threat", []), raw=raw.get("threat", {}), result_count=len(sections.get("threat", []))),
            knowledge_context=KnowledgeContext(items=sections.get("knowledge", []), raw=raw.get("knowledge", {}), result_count=len(sections.get("knowledge", []))),
            graph_context=GraphContext(items=sections.get("graph", []), raw=raw.get("graph", {}), result_count=len(sections.get("graph", []))),
            historical_context=HistoricalContext(items=sections.get("history", []), raw=raw.get("history", {}), result_count=len(sections.get("history", []))),
            graph_relationships=sections.get("graph", []), historical_similar_cases=sections.get("history", []), provenance=provenance, confidence_sources=confidence, missing_information=missing, merge_statistics=merge_statistics,
        )
        context.correlation_summary = CorrelationEngine().correlate(sections)
        context.validation = ContextValidator().validate(context)
        return context
