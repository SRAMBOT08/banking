from __future__ import annotations

from copy import deepcopy

from typing import Tuple

from app.core.logger import get_logger
from app.events import BaseEvent

logger = get_logger("normalizer")


def normalize(payload_dict: dict, original_raw: bytes) -> BaseEvent:
    """Return a canonical BaseEvent preserving original payload and identifiers."""
    # Ensure we keep original payload in metadata without creating a recursive structure.
    original_payload = deepcopy(payload_dict)
    payload_dict.setdefault("metadata", {})
    payload_dict["metadata"].setdefault("original_payload", original_payload)

    # Build BaseEvent instance
    try:
        event = BaseEvent.model_validate(payload_dict)
    except Exception as exc:
        logger.error("normalization_failed", extra={"error": str(exc)})
        raise

    return event
