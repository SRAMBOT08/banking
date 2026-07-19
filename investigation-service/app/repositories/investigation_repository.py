from __future__ import annotations
from threading import RLock
from typing import Dict, List, Optional
from app.models.investigation import Investigation
from app.repositories.base import InvestigationRepository


class InMemoryInvestigationRepository(InvestigationRepository):
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

    def find_by_tenant(self, tenant_id: str, limit: int = 100, offset: int = 0) -> List[Investigation]:
        with self._lock:
            items = [item for item in self._items.values() if item.metadata.tenant_id == tenant_id]
            items.sort(key=lambda item: item.investigation_id)
            return items[offset:offset + limit]

    def delete(self, investigation_id: str) -> bool:
        with self._lock:
            if investigation_id in self._items:
                del self._items[investigation_id]
                return True
            return False
