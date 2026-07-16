from __future__ import annotations
from typing import Dict, Optional
from .state import InvestigationState, WorkflowStatus


class StateManager:
    def __init__(self):
        self._states: Dict[str, InvestigationState] = {}

    def persist(self, state: InvestigationState) -> None:
        self._states[state.investigation_id] = state.snapshot()

    def load(self, investigation_id: str) -> InvestigationState | None:
        state = self._states.get(investigation_id)
        return state.snapshot() if state else None

    def transition(self, investigation_id: str, target: WorkflowStatus, node: Optional[str] = None) -> InvestigationState:
        state = self._require(investigation_id)
        state.transition(target, node)
        self.persist(state)
        return state

    def record_failure(self, investigation_id: str, error: str) -> InvestigationState:
        state = self._require(investigation_id)
        state.failure_count += 1
        state.execution_metadata["last_error"] = error
        state.add_history({"event": "failure", "error": error})
        self.persist(state)
        return state

    def _require(self, investigation_id: str) -> InvestigationState:
        state = self.load(investigation_id)
        if state is None:
            raise KeyError(f"Investigation is not managed: {investigation_id}")
        return state
