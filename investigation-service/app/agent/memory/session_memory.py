from __future__ import annotations
from copy import deepcopy
from typing import Any, Dict


class SessionMemory:
    def __init__(self):
        self._sessions: Dict[str, Dict] = {}

    def set(self, key: str, value: Dict[str, Any]) -> None:
        self._sessions[key] = deepcopy(value)

    def get(self, key: str) -> Dict | None:
        return deepcopy(self._sessions.get(key)) if key in self._sessions else None
