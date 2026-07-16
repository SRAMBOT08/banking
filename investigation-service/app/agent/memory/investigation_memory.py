from __future__ import annotations
from typing import Dict
from ..state import InvestigationState


class InvestigationMemory:
    def __init__(self):
        self._store: Dict[str, InvestigationState] = {}

    def persist(self, state: InvestigationState) -> None:
        self._store[state.investigation_id] = state.snapshot()

    def retrieve(self, investigation_id: str) -> InvestigationState | None:
        state = self._store.get(investigation_id)
        return state.snapshot() if state else None
