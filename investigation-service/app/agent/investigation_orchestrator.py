from __future__ import annotations
import logging
from typing import Any, Dict, Optional
from .state import InvestigationState
from .tool_router import ToolRouter
from .workflow import WorkflowEngine
from .checkpoint_manager import CheckpointManager
from .reasoning import ReasoningEngine
from .decision_engine import DecisionEngine

logger = logging.getLogger(__name__)


class InvestigationOrchestrator:
    """Orchestrates Investigation Agent execution through LangGraph workflow."""
    
    def __init__(self, tool_router: ToolRouter, graph_builder: Any):
        self.tool_router = tool_router
        self.graph_builder = graph_builder
        self._engines: Dict[str, WorkflowEngine] = {}
        
        # Components that can be set by the pipeline
        self.checkpoints: Optional[CheckpointManager] = None
        self.reasoning: Optional[ReasoningEngine] = None
        self.decision: Optional[DecisionEngine] = None

    def start(self, state: InvestigationState) -> InvestigationState:
        """Start execution of an investigation workflow."""
        logger.info("orchestrator_start", extra={"investigation_id": state.investigation_id})
        
        # Pass all available components to the graph builder
        if self.checkpoints:
            self.graph_builder.checkpoints = self.checkpoints
        if self.reasoning:
            self.graph_builder.reasoning = self.reasoning
        if self.decision:
            self.graph_builder.decision = self.decision
        
        graph = self.graph_builder.build()
        engine = WorkflowEngine(graph)
        self._engines[state.investigation_id] = engine
        result = engine.start(state)
        
        logger.info("orchestrator_end", extra={
            "investigation_id": state.investigation_id,
            "final_status": result.workflow_status.value,
        })
        return result

    def resume(self, state: InvestigationState, decision: str = "approved") -> Any:
        """Resume a paused workflow."""
        return self._engines[state.investigation_id].resume(state, decision)

    def retry(self, state: InvestigationState, reason: str) -> Any:
        """Retry a failed workflow."""
        return self._engines[state.investigation_id].retry(state, reason)

    def cancel(self, state: InvestigationState) -> InvestigationState:
        """Cancel an active workflow."""
        return self._engines[state.investigation_id].cancel(state)
