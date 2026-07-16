from __future__ import annotations

import logging
from typing import Optional

from .models import (
    EntityDetails,
    EvidenceDetails,
    EvidenceQueryRequest,
    EvidenceSearchResult,
    EvidenceStatistics,
    EvidenceSummary,
    EvidenceTimeline,
    RelationshipDetails,
    EvidenceValidation,
)
from .repository import EvidenceRepository

logger = logging.getLogger("sentineliq.evidence.query")


class EvidenceQueryService:
    """Application read service for processed Evidence data."""

    def __init__(self, repository: EvidenceRepository):
        self._repository = repository

    def get_evidence(self, evidence_id: str) -> Optional[EvidenceDetails]:
        logger.info({"event": "evidence_query", "operation": "find_by_id", "evidence_id": evidence_id})
        return self._repository.find_by_id(evidence_id)

    def get_entity(self, entity_id: str) -> Optional[EntityDetails]:
        logger.info({"event": "evidence_query", "operation": "find_entity", "entity_id": entity_id})
        return self._repository.find_entity(entity_id)

    def get_by_entity(self, entity_id: str) -> list[EvidenceDetails]:
        logger.info({"event": "evidence_query", "operation": "find_by_entity", "entity_id": entity_id})
        return self._repository.find_by_entity(entity_id)

    def get_relationships(self, evidence_id: str) -> list[RelationshipDetails]:
        logger.info({"event": "evidence_query", "operation": "find_relationships", "evidence_id": evidence_id})
        return self._repository.find_relationships(evidence_id)

    def get_timeline(self, request: EvidenceQueryRequest) -> EvidenceTimeline:
        logger.info({"event": "evidence_query", "operation": "find_timeline", "investigation_id": request.investigation_id})
        return self._repository.find_timeline(request)

    def get_metadata(self, evidence_id: str) -> Optional[EvidenceSummary]:
        logger.info({"event": "evidence_query", "operation": "find_metadata", "evidence_id": evidence_id})
        return self._repository.find_metadata(evidence_id)

    def validate(self, evidence_id: str) -> Optional[EvidenceValidation]:
        logger.info({"event": "evidence_query", "operation": "validate", "evidence_id": evidence_id})
        return self._repository.validate(evidence_id)

    def search(self, request: EvidenceQueryRequest) -> EvidenceSearchResult:
        return self._repository.search(request)

    def statistics(self) -> EvidenceStatistics:
        logger.info({"event": "evidence_query", "operation": "statistics"})
        return self._repository.statistics()
