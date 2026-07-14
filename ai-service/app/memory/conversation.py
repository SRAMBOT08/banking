from __future__ import annotations
from datetime import datetime, timezone
from threading import RLock
from typing import Any, Dict, List


class ConversationMemory:
    """AI-only process-local conversation and usage history."""
    def __init__(self):
        self._items: Dict[str, List[Dict[str, Any]]] = {}
        self._lock = RLock()

    def append(self, investigation_id: str, item: Dict[str, Any]) -> None:
        with self._lock:
            self._items.setdefault(investigation_id, []).append({**item, "timestamp": datetime.now(timezone.utc).isoformat()})

    def list(self, investigation_id: str) -> List[Dict[str, Any]]:
        with self._lock:
            return [dict(item) for item in self._items.get(investigation_id, [])]

    def all(self) -> Dict[str, List[Dict[str, Any]]]:
        with self._lock:
            return {key: [dict(item) for item in values] for key, values in self._items.items()}
