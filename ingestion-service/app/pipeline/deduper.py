from __future__ import annotations

from typing import Optional

from app.infrastructure.dedupe import deterministic_checksum, DedupeStore
from app.core.logger import get_logger

logger = get_logger("deduper")


class DuplicateEvent(Exception):
    pass


class Deduper:
    def __init__(self, store: DedupeStore, window_seconds: int = 60 * 5):
        self.store = store
        self.window = window_seconds

    async def is_duplicate(self, event_id: str, normalized_payload: dict, stable_metadata: Optional[dict] = None) -> bool:
        # priority 1: event_id
        if event_id:
            key = f"eid:{event_id}"
            dup = await self.store.check_and_set(key, self.window)
            if dup:
                logger.info("duplicate_event", extra={"reason": "event_id", "event_id": event_id})
                return True

        # priority 2: checksum
        checksum = deterministic_checksum(normalized_payload, stable_metadata)
        key = f"chk:{checksum}"
        dup = await self.store.check_and_set(key, self.window)
        if dup:
            logger.info("duplicate_event", extra={"reason": "checksum", "checksum": checksum})
            return True

        return False
