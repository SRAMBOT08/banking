from __future__ import annotations
import logging
from typing import Dict, Any
from .state import InvestigationState

logger = logging.getLogger(__name__)


def build_graph_definition() -> Dict[str, Any]:
    """Produce a LangGraph-compatible graph definition.

    The concrete construction depends on the project's LangGraph version and
    will be assembled in the service bootstrap code where DI supplies Tools.
    Returning a dictionary makes it easy to test and introspect.
    """
    logger.debug("building langgraph graph definition")
    return {
        "start": "collect_evidence",
        "nodes": [
            "collect_evidence",
            # other nodes will be added by planner as implementation progresses
        ],
    }


def plan(state: InvestigationState) -> Dict[str, Any]:
    """High level plan used by the orchestration layer to decide which workflow to run."""
    logger.info({"event": "plan_created", "investigation_id": state.investigation_id})
    return build_graph_definition()
