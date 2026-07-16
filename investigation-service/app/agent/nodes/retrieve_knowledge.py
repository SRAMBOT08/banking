from __future__ import annotations
from typing import Any
from ..state import InvestigationState, WorkflowStatus
from ..tool_router import ToolRouter
from .common import run_node

def retrieve_knowledge(state: InvestigationState, router: ToolRouter, params: dict[str, Any] | None = None) -> InvestigationState:
    from ...aggregation import IntelligenceAggregator

    def apply(current: InvestigationState, result: Any) -> None:
        context = result.model_dump(mode="json")
        current.intelligence_context = context
        current.knowledge = context.get("knowledge_context", {})
        current.evidence = context.get("evidence_context", {}).get("items", current.evidence)
        current.matched_patterns = context.get("threat_context", {}).get("items", current.matched_patterns)
        current.graph_results = context.get("graph_context", {})
        current.metadata["historical_investigations"] = context.get("historical_context", {}).get("items", [])
        current.tool_outputs["investigation_context"] = context
        current.tool_outputs["knowledge"] = current.knowledge
    context = IntelligenceAggregator(router).aggregate(state, params)
    return run_node(state, router, "retrieve_knowledge", WorkflowStatus.PATTERN_MATCHING, None, {}, lambda current, _: apply(current, context))
