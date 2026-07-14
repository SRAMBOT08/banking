from __future__ import annotations
from copy import deepcopy
from typing import Callable, List, Optional
from app.models.investigation import Investigation, ConfidenceHistory
from app.models.memory import InvestigationMemoryEvent
from app.services.memory import InvestigationMemory


class InvestigationReplay:
    def __init__(self, memory: InvestigationMemory):
        self.memory = memory

    def events(self, investigation_id: str, event_type: Optional[str] = None) -> List[InvestigationMemoryEvent]:
        events = self.memory.list(investigation_id)
        return [event for event in events if event_type is None or event.event_type == event_type]

    def replay(self, investigation: Investigation, event_type: Optional[str] = None) -> Investigation:
        result = deepcopy(investigation)
        events = self.events(investigation.investigation_id, event_type)
        result.state_history = []
        result.confidence_history = []
        for event in events:
            if event.event_type == "STATE_CHANGED":
                result.state_history.append(event.payload)
            elif event.event_type == "CONFIDENCE_UPDATED":
                payload = dict(event.payload)
                payload.setdefault("timestamp", event.timestamp)
                payload.setdefault("reason", "Confidence updated")
                result.confidence_history.append(ConfidenceHistory.model_validate(payload))
        return result
