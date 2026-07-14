
from __future__ import annotations

from typing import Dict, List

from app.core.logger import get_logger
from app.events import BaseEvent

logger = get_logger("extractor")


SUPPORTED_ENTITIES = [
    "user",
    "organization",
    "account",
    "device",
    "ip",
    "session",
    "transaction",
    "beneficiary",
    "threat_indicator",
    "asset",
    "alert",
    "evidence",
]


def extract(event: BaseEvent) -> Dict[str, List[Dict]]:
    """Deterministically extract entities from a normalized BaseEvent.

    This function uses simple, deterministic rules: it looks for well-known keys
    in the event payload and maps them to entities.
    """
    out = {k: [] for k in SUPPORTED_ENTITIES}
    payload = getattr(event, "metadata", {}) or {}
    # simple mappings
    if payload.get("user_id"):
        out["user"].append({"id": payload["user_id"], "source": event.source_id})
    if payload.get("user_name"):
        out["user"].append({"username": payload["user_name"], "source": event.source_id})
    if payload.get("org_id"):
        out["organization"].append({"id": payload["org_id"], "source": event.source_id})
    if payload.get("account_id"):
        out["account"].append({"id": payload["account_id"], "source": event.source_id})
    if payload.get("device_id"):
        out["device"].append({"id": payload["device_id"], "source": event.source_id})
    if payload.get("ip"):
        out["ip"].append({"address": payload["ip"], "source": event.source_id})
    if payload.get("session_id"):
        out["session"].append({"id": payload["session_id"], "source": event.source_id})
    if payload.get("transaction_id"):
        out["transaction"].append({"id": payload["transaction_id"], "source": event.source_id})
    if payload.get("beneficiary_id"):
        out["beneficiary"].append({"id": payload["beneficiary_id"], "source": event.source_id})
    if payload.get("threat_indicator"):
        out["threat_indicator"].append({"value": payload["threat_indicator"], "source": event.source_id})
    if payload.get("asset_id"):
        out["asset"].append({"id": payload["asset_id"], "source": event.source_id})
    if payload.get("alert_id"):
        out["alert"].append({"id": payload["alert_id"], "source": event.source_id})
    # evidence - preserve original event as evidence
    out["evidence"].append({"event_id": str(event.event_id), "source": event.source_id})

    logger.info("extraction_complete", extra={"counts": {k: len(v) for k, v in out.items()}})
    return out
