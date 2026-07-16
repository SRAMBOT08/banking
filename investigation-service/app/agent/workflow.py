from __future__ import annotations
from typing import Any, Dict, Optional
from langgraph.types import Command
from .state import InvestigationState, WorkflowStatus


class WorkflowEngine:
    def __init__(self, graph: Any, config: Optional[Dict[str, Any]] = None):
        self.graph, self.config = graph, config or {}

    def start(self, state: InvestigationState) -> Any:
        return self._unwrap(self.graph.invoke({"state": state.model_dump(mode="json")}, config=self._config(state)))

    def resume(self, state: InvestigationState, decision: str = "approved") -> Any:
        return self._unwrap(self.graph.invoke(Command(resume=decision), config=self._config(state)))

    def retry(self, state: InvestigationState, reason: str) -> Any:
        state.record_retry(reason)
        return self._unwrap(self.graph.invoke({"state": state.model_dump(mode="json")}, config=self._config(state)))

    def cancel(self, state: InvestigationState) -> InvestigationState:
        if state.workflow_status not in {WorkflowStatus.COMPLETED, WorkflowStatus.CANCELLED}:
            state.transition(WorkflowStatus.CANCELLED, "workflow")
        return state

    def _config(self, state: InvestigationState) -> Dict[str, Any]:
        return {**self.config, "configurable": {**self.config.get("configurable", {}), "thread_id": state.investigation_id}}

    @staticmethod
    def _unwrap(result: Any) -> Any:
        if isinstance(result, dict) and "state" in result:
            return InvestigationState.model_validate(result["state"])
        return result


def run_workflow(state: InvestigationState, graph: Any, tool_router: Any = None) -> InvestigationState:
    return WorkflowEngine(graph).start(state)
