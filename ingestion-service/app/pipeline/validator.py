from __future__ import annotations

import re
from datetime import datetime
from uuid import UUID
from typing import Tuple

from app.core.logger import get_logger
from app.events import BaseEvent, EventRegistry

logger = get_logger("validator")


class ValidationError(Exception):
    pass


UUID_RE = re.compile(r"^[0-9a-fA-F-]{36}$")


def _is_valid_uuid(val: str) -> bool:
    try:
        UUID(val)
        return True
    except Exception:
        return False


def validate_raw_message(raw: bytes) -> Tuple[dict, BaseEvent]:
    """Validate raw incoming message bytes. Returns (payload_dict, event_model) on success or raises ValidationError."""
    try:
        payload = BaseEvent.model_validate_json(raw)
    except Exception as exc:
        logger.error("validation_failed", extra={"reason": "invalid_json", "error": str(exc)})
        raise ValidationError("invalid_json")

    # payload is a BaseEvent instance
    if not getattr(payload, "event_type", None):
        logger.error("validation_failed", extra={"reason": "missing_event_type"})
        raise ValidationError("missing_event_type")

    if not getattr(payload, "event_version", None):
        logger.error("validation_failed", extra={"reason": "missing_event_version"})
        raise ValidationError("missing_event_version")

    # UUIDs
    if not _is_valid_uuid(str(payload.event_id)):
        logger.error("validation_failed", extra={"reason": "invalid_event_id", "event_id": str(payload.event_id)})
        raise ValidationError("invalid_event_id")

    # timestamp validity
    try:
        datetime.fromisoformat(str(payload.timestamp))
    except Exception:
        logger.error("validation_failed", extra={"reason": "invalid_timestamp", "timestamp": str(payload.timestamp)})
        raise ValidationError("invalid_timestamp")

    # tenant and source
    if not getattr(payload, "tenant_id", None):
        logger.error("validation_failed", extra={"reason": "missing_tenant_id"})
        raise ValidationError("missing_tenant_id")
    if not getattr(payload, "source_id", None):
        logger.error("validation_failed", extra={"reason": "missing_source_id"})
        raise ValidationError("missing_source_id")

    # event registry check
    try:
        EventRegistry.get_event(payload.event_type, payload.event_version)
    except Exception:
        logger.error("validation_failed", extra={"reason": "unknown_event_type", "event_type": payload.event_type, "event_version": payload.event_version})
        raise ValidationError("unknown_event_type")

    return payload.model_dump(), payload
