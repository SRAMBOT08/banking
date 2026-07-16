from __future__ import annotations

import logging
from .models import *
from .repository import InvestigationMemoryRepository

logger = logging.getLogger("sentineliq.memory.query")


class InvestigationMemoryQueryService:
    """Read-only application service delegating to repository/engine boundaries."""

    def __init__(self, repository: InvestigationMemoryRepository):
        self.repository = repository

    def _log(self, operation: str, **extra):
        logger.info({"event": "memory_query", "operation": operation, **extra})

    def lookup(self, investigation_id: str):
        result = self.repository.find_investigation(investigation_id)
        self._log("lookup", investigation_id=investigation_id, result_count=int(result is not None))
        return result

    def search(self, request: InvestigationSearchRequest):
        result = self.repository.find_historical_cases(request)
        self._log("search", result_count=len(result.items))
        return result

    def similarity(self, request: SimilarityRequest):
        result = self.repository.find_similar(request)
        self._log("similarity", similarity_score=result.overall_score, matched_investigations=len(result.matching_investigation_ids))
        return result

    def timeline(self, entity_id: str, timeline_type: str = "entity"):
        result = self.repository.find_timeline(entity_id, timeline_type)
        self._log("timeline", entity_id=entity_id, result_count=len(result.events))
        return result

    def outcome(self, investigation_id: str):
        return self.repository.find_outcome(investigation_id)

    def resolution(self, investigation_id: str):
        return self.repository.find_resolution(investigation_id)

    def lessons(self, investigation_id: str):
        return self.repository.find_lessons_learned(investigation_id)

    def related(self, investigation_id: str):
        return self.repository.find_related(investigation_id)

    def historical_evidence(self, investigation_id: str):
        return self.repository.find_historical_evidence(investigation_id)

    def historical_threat(self, investigation_id: str):
        return self.repository.find_historical_threat(investigation_id)

    def historical_knowledge(self, investigation_id: str):
        return self.repository.find_historical_knowledge(investigation_id)

    def historical_graph(self, investigation_id: str):
        return self.repository.find_historical_graph(investigation_id)

    def statistics(self):
        return self.repository.statistics()

    def metadata(self):
        return self.repository.metadata()
