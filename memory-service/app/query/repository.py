from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Optional
from shared.query import BaseQueryRepository
from .models import *


class InvestigationMemoryRepository(BaseQueryRepository[InvestigationSearchRequest, InvestigationSearchResponse], ABC):
    @abstractmethod
    def find_investigation(self, investigation_id: str) -> Optional[InvestigationRecord]: ...

    @abstractmethod
    def find_similar(self, request: SimilarityRequest) -> InvestigationSimilarity: ...

    @abstractmethod
    def find_historical_cases(self, request: InvestigationSearchRequest) -> InvestigationSearchResponse: ...

    @abstractmethod
    def find_timeline(self, entity_id: str, timeline_type: str = "entity") -> InvestigationTimeline: ...

    @abstractmethod
    def find_outcome(self, investigation_id: str) -> Optional[InvestigationOutcome]: ...

    @abstractmethod
    def find_resolution(self, investigation_id: str) -> Optional[ResolutionPattern]: ...

    @abstractmethod
    def find_lessons_learned(self, investigation_id: str) -> Optional[LessonsLearned]: ...

    @abstractmethod
    def find_related(self, investigation_id: str) -> List[InvestigationSummary]: ...

    @abstractmethod
    def find_historical_evidence(self, investigation_id: str) -> List[HistoricalEvidence]: ...

    @abstractmethod
    def find_historical_threat(self, investigation_id: str) -> List[HistoricalThreat]: ...

    @abstractmethod
    def find_historical_knowledge(self, investigation_id: str) -> List[HistoricalKnowledge]: ...

    @abstractmethod
    def find_historical_graph(self, investigation_id: str) -> List[HistoricalGraph]: ...

    @abstractmethod
    def statistics(self) -> InvestigationStatistics: ...

    @abstractmethod
    def metadata(self) -> MemoryMetadata: ...
