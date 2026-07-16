from __future__ import annotations

from typing import Any, Dict, Optional


class WorkflowMemory:
    def __init__(self) -> None:
        self._records: Dict[str, Dict[str, Any]] = {}

    def record(self, workflow_id: str, event: Dict[str, Any]) -> None:
        self._records.setdefault(workflow_id, {"events": []})["events"].append(dict(event))

    def get(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        record = self._records.get(workflow_id)
        return {"events": list(record["events"])} if record else None
