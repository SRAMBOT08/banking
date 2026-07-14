from __future__ import annotations
from typing import Iterable, List, Set
from app.models.investigation import InvestigationEvidence


CORRELATION_KEYS = ("user_id", "device_id", "account_id", "ip", "ip_address", "session_id", "transaction_id")


def entity_keys(evidence: Iterable[InvestigationEvidence]) -> Set[str]:
    keys = set()
    for item in evidence:
        for key in CORRELATION_KEYS:
            value = item.properties.get(key)
            if value is not None:
                keys.add(f"{key}:{value}")
    return keys


def correlation_strength(existing: Iterable[InvestigationEvidence], incoming: Iterable[InvestigationEvidence]) -> int:
    left, right = entity_keys(existing), entity_keys(incoming)
    if not left or not right:
        return 0
    shared = len(left & right)
    return min(100, shared * 25)
