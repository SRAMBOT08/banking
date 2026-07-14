from __future__ import annotations
from threading import RLock
from typing import Dict, List, Optional
from app.models.investigation import Investigation


class InMemoryInvestigationRepository:
    def __init__(self):
        self._items: Dict[str, Investigation] = {}
        self._lock = RLock()

    def save(self, investigation: Investigation) -> Investigation:
        with self._lock:
            self._items[investigation.investigation_id] = investigation
            return investigation

    def get(self, investigation_id: str) -> Optional[Investigation]:
        with self._lock:
            return self._items.get(investigation_id)

    def list_all(self) -> List[Investigation]:
        with self._lock:
            return sorted(self._items.values(), key=lambda item: item.investigation_id)

    def find_by_correlation(self, correlation_id: str) -> List[Investigation]:
        return [item for item in self.list_all() if correlation_id in item.metadata.correlation_ids]
