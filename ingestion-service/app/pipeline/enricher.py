from __future__ import annotations

from datetime import datetime
from typing import Optional

from app.core.logger import get_logger
from app.events import BaseEvent

logger = get_logger("enricher")


def enrich(event: BaseEvent, producer_service: Optional[str] = None, schema_version: Optional[str] = None) -> BaseEvent:
    # populate ingestion timestamp
    if not getattr(event, "ingestion_timestamp", None):
        event.ingestion_timestamp = datetime.utcnow().isoformat() + "Z"

    if not getattr(event, "producer_service", None) and producer_service:
        event.producer_service = producer_service

    if not getattr(event, "schema_version", None) and schema_version:
        event.schema_version = schema_version

    # correlation and trace id defaults
    if not getattr(event, "correlation_id", None):
        event.correlation_id = event.event_id
    if not getattr(event, "trace_id", None):
        event.trace_id = event.event_id

    return event
