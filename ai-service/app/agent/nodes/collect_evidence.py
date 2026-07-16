from __future__ import annotations
import logging
from typing import Dict, Any
from ..state import InvestigationState
from ..tools.interfaces import EvidenceTool

logger = logging.getLogger(__name__)


def collect_evidence(state: InvestigationState, evidence_tool: EvidenceTool, params: Dict[str, Any]) -> InvestigationState:
    """Node: Collect evidence

    Calls the EvidenceTool to fetch evidence and updates the InvestigationState.
    This node is deterministic and contains no business logic beyond orchestration.
    """
    node_name = "collect_evidence"
    logger.info({"event": "node_start", "node": node_name, "investigation_id": state.investigation_id})
    state.current_step = node_name
    try:
        updated = evidence_tool.collect(state, params)
        updated.add_history({"node": node_name, "action": "collected", "params": params})
        logger.info({"event": "node_end", "node": node_name, "investigation_id": state.investigation_id, "evidence_count": len(updated.evidence)})
        return updated
    except Exception as exc:
        logger.exception({"event": "node_error", "node": node_name, "error": str(exc)})
        raise
