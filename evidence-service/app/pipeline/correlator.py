from __future__ import annotations

from datetime import datetime, timedelta
from typing import Dict, List, Any

from app.core.logger import get_logger

logger = get_logger("correlator")


def correlate(event: Any, resolved_entities: Dict[str, list], window_seconds: int = 300) -> Dict[str, Any]:
    """Produce a correlation group deterministically based on correlation_id, investigation_id, and entity overlap."""
    groups = []
    correlation_id = getattr(event, "correlation_id", None)
    investigation_id = getattr(event, "investigation_id", None)
    ts = getattr(event, "timestamp", None)

    group = {
        "correlation_id": correlation_id,
        "investigation_id": investigation_id,
        "entities": [],
        "time": ts,
    }

    for etype, items in resolved_entities.items():
        for it in items:
            group["entities"].append({"type": etype, "canonical_id": it["canonical_id"]})

    logger.info("correlation_complete", extra={"entities": len(group["entities"])})
    return group
