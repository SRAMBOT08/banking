from __future__ import annotations
from typing import Dict, Any, List
from app.core.logger import get_logger

logger = get_logger("inmemory_repo")


class InMemoryGraphRepo:
    def __init__(self):
        self.nodes: Dict[str, Dict[str, Any]] = {}
        self.relationships: List[Dict[str, Any]] = []

    def save_pattern_match(self, candidate: Dict[str, Any]):
        # store candidate by id
        self.nodes[candidate["candidate_id"]] = candidate
        logger.info("candidate_saved", extra={"candidate_id": candidate["candidate_id"]})

    def list_candidates(self):
        return list(self.nodes.values())
