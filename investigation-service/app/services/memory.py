from __future__ import annotations
from threading import RLock
from typing import Any, Dict, List, Optional
from app.core.logger import get_logger
from app.models.investigation import Investigation
from app.models.memory import InvestigationMemoryEvent

logger = get_logger("investigation_memory")


class InvestigationMemory:
    """Append-only process-local memory for complete investigation history."""
    def __init__(self):
        self._events: Dict[str, List[InvestigationMemoryEvent]] = {}
        self._lock = RLock()

    def append(self, investigation: Investigation, event_type: str, payload: Dict[str, Any], timestamp: Optional[str] = None) -> InvestigationMemoryEvent:
        with self._lock:
            events = self._events.setdefault(investigation.investigation_id, [])
            event = InvestigationMemoryEvent.create(investigation.investigation_id, event_type, len(events) + 1, payload, timestamp,
                                                     investigation.metadata.tenant_id,
                                                     investigation.metadata.correlation_ids[0] if investigation.metadata.correlation_ids else None)
            events.append(event)
            logger.info("memory_event_appended", extra={"investigation_id": investigation.investigation_id, "event_type": event_type, "sequence": event.sequence})
            return event

    def list(self, investigation_id: str) -> List[InvestigationMemoryEvent]:
        with self._lock:
            return list(self._events.get(investigation_id, []))

    def related(self, investigation_id: str) -> List[str]:
        events = self.list(investigation_id)
        ids = {str(event.payload.get("related_investigation_id")) for event in events if event.payload.get("related_investigation_id")}
        return sorted(ids - {investigation_id})
