from __future__ import annotations

from abc import ABC, abstractmethod
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


class EvidenceRepository(ABC):
    """Read-only repository contract for processed Evidence data."""

    @abstractmethod
    def find_by_id(self, evidence_id: str) -> Optional[EvidenceDetails]:
        raise NotImplementedError()

    @abstractmethod
    def find_entity(self, entity_id: str) -> Optional[EntityDetails]:
        raise NotImplementedError()

    @abstractmethod
    def find_by_entity(self, entity_id: str) -> list[EvidenceDetails]:
        raise NotImplementedError()

    @abstractmethod
    def find_relationships(self, evidence_id: str) -> list[RelationshipDetails]:
        raise NotImplementedError()

    @abstractmethod
    def find_timeline(self, request: EvidenceQueryRequest) -> EvidenceTimeline:
        raise NotImplementedError()

    @abstractmethod
    def find_metadata(self, evidence_id: str) -> Optional[EvidenceSummary]:
        raise NotImplementedError()

    @abstractmethod
    def validate(self, evidence_id: str) -> Optional[EvidenceValidation]:
        raise NotImplementedError()

    @abstractmethod
    def search(self, request: EvidenceQueryRequest) -> EvidenceSearchResult:
        raise NotImplementedError()

    @abstractmethod
    def statistics(self) -> EvidenceStatistics:
        raise NotImplementedError()
