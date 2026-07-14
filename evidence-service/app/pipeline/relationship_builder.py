from __future__ import annotations

from typing import Dict, List

from app.core.logger import get_logger

logger = get_logger("relationship_builder")


RELATIONSHIP_MAP = [
    ("user", "ip", "USES_IP"),
    ("user", "device", "USES_DEVICE"),
    ("account", "transaction", "INITIATED"),
    ("transaction", "beneficiary", "SENT_TO"),
    ("user", "organization", "OWNS"),
]


def build_relationships(resolved: Dict[str, list]) -> List[Dict]:
    rels = []
    # naive deterministic pairing: for each map, connect first entity of each type if present
    for a, b, rel in RELATIONSHIP_MAP:
        if resolved.get(a) and resolved.get(b):
            rels.append({
                "type": rel,
                "from": resolved[a][0]["canonical_id"],
                "to": resolved[b][0]["canonical_id"],
            })

    logger.info("relationships_built", extra={"count": len(rels)})
    return rels
