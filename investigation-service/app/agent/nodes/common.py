from __future__ import annotations
import logging
from functools import wraps
from typing import Any, Callable, Dict
from ..state import InvestigationState, NodeExecution, WorkflowStatus
from ..tool_router import ToolRouter


def node_logger(node: str, state: InvestigationState, execution: NodeExecution, event: str, **extra: Any) -> None:
    logging.getLogger(f"sentineliq.agent.node.{node}").info({"event": event, "investigation_id": state.investigation_id, "node": node, "previous_node": execution.previous_node, "retry_count": state.retry_count, "checkpoint_id": state.checkpoint_id, **extra})


NODE_STATUS = {
    "collect_evidence": WorkflowStatus.COLLECTING_EVIDENCE,
    "retrieve_knowledge": WorkflowStatus.KNOWLEDGE_RETRIEVAL,
    "run_pattern_matching": WorkflowStatus.PATTERN_MATCHING,
    "identify_missing_evidence": WorkflowStatus.PATTERN_MATCHING,
    "graph_analysis": WorkflowStatus.GRAPH_ANALYSIS,
    "retrieve_history": WorkflowStatus.HISTORY_ANALYSIS,
    "generate_hypotheses": WorkflowStatus.HYPOTHESIS_GENERATION,
    "aggregate_confidence": WorkflowStatus.CONFIDENCE_AGGREGATION,
    "decision_engine": WorkflowStatus.DECISION_ENGINE,
    "human_approval": WorkflowStatus.WAITING_FOR_APPROVAL,
    "build_investigation": WorkflowStatus.REPORT_GENERATION,
    "generate_ai_report": WorkflowStatus.REPORT_GENERATION,
    "execution_planning": WorkflowStatus.EXECUTION_PLANNING,
}


def run_node(state: InvestigationState, router: ToolRouter, node: str, target: WorkflowStatus, tool: str | None, params: Dict[str, Any], apply_result: Callable[[InvestigationState, Any], None]) -> InvestigationState:
    execution = state.begin_node(node)
    node_logger(node, state, execution, "node_start", tool=tool)
    try:
        node_status = NODE_STATUS[node]
        if state.workflow_status != node_status and node_status in state.ALLOWED_TRANSITIONS.get(state.workflow_status, set()):
            state.transition(node_status, node)
        result = router.invoke(tool, state, params) if tool else None
        apply_result(state, result)
        if state.workflow_status != target and target in state.ALLOWED_TRANSITIONS.get(state.workflow_status, set()):
            state.transition(target, node)
        state.finish_node(execution)
        
        # Update execution metadata with progress after each node
        state.update_execution_metadata()
        progress = state.get_progress_percent()
        
        node_logger(node, state, execution, "node_finish", execution_time_ms=execution.duration_ms, state_changes=list(state.tool_outputs), progress_percent=progress)
        return state
    except Exception as exc:
        state.finish_node(execution, "failed", str(exc))
        state.update_execution_metadata()
        node_logger(node, state, execution, "node_error", error=str(exc))
        raise
