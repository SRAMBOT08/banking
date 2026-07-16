from __future__ import annotations

from datetime import datetime, timezone
from time import perf_counter
from typing import Any

from ..agent.state import InvestigationState
from ..agent.tool_router import ToolRouter
from .confidence_tracker import ConfidenceTracker
from .context_builder import ContextBuilder
from .models import InvestigationContext
from .normalizer import IntelligenceNormalizer
from .provenance_tracker import ProvenanceTracker


class IntelligenceAggregator:
    """Single deterministic entry point for the five intelligence sources."""

    SOURCES = ("evidence", "threat", "knowledge", "graph", "memory")

    def __init__(self, router: ToolRouter):
        self.router = router
        self.normalizer = IntelligenceNormalizer()

    def _invoke(self, source: str, state: InvestigationState, params: dict[str, Any]) -> Any:
        if source == "graph":
            return self.router.invoke(source, params.get("query", ""), params)
        if source == "threat":
            return self.router.invoke(source, state, params)
        return self.router.invoke(source, state, params)

    def aggregate(self, state: InvestigationState, params: dict[str, Any] | None = None) -> InvestigationContext:
        started = perf_counter()
        params = params or {}
        raw: dict[str, Any] = {}
        sections: dict[str, list[dict[str, Any]]] = {}
        missing: list[str] = []
        provenance = []
        confidence = []
        correlation_id = str(state.metadata.get("correlation_id") or state.investigation_id)
        source_params = {
            "evidence": params.get("evidence", {}),
            "threat": params.get("threat", {"evidence": state.evidence}),
            "knowledge": params.get("knowledge", {"evidence": state.evidence}),
            "graph": params.get("graph", {"query": "", "investigation_id": state.investigation_id}),
            "memory": params.get("memory", {}),
        }
        keys = {"evidence": ("evidence",), "threat": ("threats", "patterns", "matched_patterns"), "knowledge": ("patterns", "knowledge"), "graph": ("relationships", "nodes"), "memory": ("historical_investigations", "similar_cases", "results")}
        for source in self.SOURCES:
            try:
                value = self._invoke(source, state, source_params[source])
            except Exception as exc:
                raw[source] = {"error": str(exc)}
                sections[source if source != "memory" else "history"] = []
                missing.append(source)
                continue
            raw[source] = value if isinstance(value, dict) else {"items": value}
            section = source if source != "memory" else "history"
            items, _ = self.normalizer.normalize_payload(value, source, keys[source])
            sections[section] = items
            for item in items:
                provenance.append(ProvenanceTracker().record(service=source, fact=item, investigation_id=state.investigation_id, correlation_id=correlation_id, workflow_id=state.metadata.get("workflow_id")))
            confidence.append(ConfidenceTracker().record(source, items))
        from .merge_engine import DeterministicMergeEngine
        merged, statistics = DeterministicMergeEngine().merge(sections)
        context = ContextBuilder().build(state=state, sections=merged, raw=raw, provenance=provenance, confidence=confidence, merge_statistics=statistics, missing=missing)
        context.metadata.aggregation_duration_ms = (perf_counter() - started) * 1000
        context.context_metadata.update({"aggregated_at": datetime.now(timezone.utc).isoformat(), "source_count": len(self.SOURCES) - len(missing)})
        return context

    __call__ = aggregate
