from __future__ import annotations
from typing import Dict, Any, List
from app.core.logger import get_logger

logger = get_logger("candidates_repo")


class InMemoryCandidatesRepo:
    def __init__(self):
        self._store: Dict[str, Dict[str, Any]] = {}

    def save(self, candidate: Dict[str, Any]):
        self._store[candidate['candidate_id']] = candidate
        logger.info("candidate_saved", extra={"candidate_id": candidate['candidate_id']})

    def list_all(self) -> List[Dict[str, Any]]:
        return list(self._store.values())
