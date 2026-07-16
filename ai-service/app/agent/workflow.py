from __future__ import annotations
import logging
from typing import Any, Dict
from .state import InvestigationState

logger = logging.getLogger(__name__)


def run_workflow(state: InvestigationState, graph: Any) -> InvestigationState:
    """Execute a LangGraph workflow graph against the provided InvestigationState.

    This function is intentionally small: LangGraph will orchestrate node execution.
    The `graph` parameter is expected to be a LangGraph graph object created elsewhere
    and wired with concrete tool implementations.
    """
    logger.info({"event": "workflow_start", "investigation_id": state.investigation_id})
    result = graph.run(state)  # graph is responsible for node sequencing and checkpoints
    logger.info({"event": "workflow_end", "investigation_id": state.investigation_id})
    return result
