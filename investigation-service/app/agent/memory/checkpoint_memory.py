from __future__ import annotations
from typing import Dict
from ..state import InvestigationState


class CheckpointMemory:
    def __init__(self):
        self._checkpoints: Dict[str, InvestigationState] = {}

    def save(self, state: InvestigationState) -> None:
        self._checkpoints[state.investigation_id] = state.copy(deep=True)

    def load(self, investigation_id: str) -> InvestigationState | None:
        return self._checkpoints.get(investigation_id)
