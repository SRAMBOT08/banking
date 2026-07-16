from __future__ import annotations

from typing import Any, Dict, List


class ExecutionMemory:
    def __init__(self) -> None:
        self._records: Dict[str, List[Dict[str, Any]]] = {}

    def record(self, investigation_id: str, execution: Dict[str, Any]) -> None:
        self._records.setdefault(investigation_id, []).append(dict(execution))

    def list(self, investigation_id: str) -> List[Dict[str, Any]]:
        return list(self._records.get(investigation_id, []))
