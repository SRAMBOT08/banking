from __future__ import annotations

import hashlib
from typing import Dict, Any

from app.core.logger import get_logger

logger = get_logger("resolver")


def canonical_id(entity_type: str, identity: Dict[str, Any]) -> str:
    """Deterministic canonical id: sha256 of entity_type + sorted keys/values of identity."""
    s = entity_type + "|"
    items = sorted(identity.items())
    for k, v in items:
        s += f"{k}:{v}|"
    return hashlib.sha256(s.encode()).hexdigest()


def resolve_entities(extracted: Dict[str, list]) -> Dict[str, list]:
    """Resolve entities to canonical forms with source mapping and canonical ids."""
    resolved = {}
    for etype, items in extracted.items():
        resolved[etype] = []
        for it in items:
            cid = canonical_id(etype, it)
            resolved[etype].append({"canonical_id": cid, "attributes": it})
    logger.info("resolution_complete", extra={"counts": {k: len(v) for k, v in resolved.items()}})
    return resolved
