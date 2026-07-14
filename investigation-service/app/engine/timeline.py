from __future__ import annotations
from typing import Iterable
from app.models.investigation import Investigation, TimelineEvent


def add_timeline_event(investigation: Investigation, event: TimelineEvent) -> None:
    if not any(item.event_id == event.event_id for item in investigation.timeline.events):
        investigation.timeline.events.append(event)
    investigation.timeline.events.sort(key=lambda item: (item.timestamp, item.event_id))
