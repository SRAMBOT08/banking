from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional
from shared.query import BaseQueryRepository

from .models import (
    ThreatDetails,
    ThreatIndicator,
    ThreatMetadata,
    ThreatPattern,
    ThreatSearchRequest,
    ThreatSearchResult,
    ThreatStatistics,
    ThreatValidation,
)


class ThreatRepository(BaseQueryRepository[ThreatSearchRequest, ThreatSearchResult], ABC):
    """Read-only repository contract for processed Threat Intelligence."""

    @abstractmethod
    def find_pattern(self, pattern: str, version: Optional[str] = None) -> Optional[ThreatPattern]:
        raise NotImplementedError()

    @abstractmethod
    def find_indicator(self, indicator: str) -> Optional[ThreatIndicator]:
        raise NotImplementedError()

    @abstractmethod
    def find_threat(self, threat_id: str) -> Optional[ThreatDetails]:
        raise NotImplementedError()

    @abstractmethod
    def find_attack(self, attack: str, version: Optional[str] = None) -> Optional[ThreatPattern]:
        raise NotImplementedError()

    @abstractmethod
    def find_metadata(self) -> ThreatMetadata:
        raise NotImplementedError()

    @abstractmethod
    def validate(self) -> ThreatValidation:
        raise NotImplementedError()

    @abstractmethod
    def search(self, request: ThreatSearchRequest) -> ThreatSearchResult:
        raise NotImplementedError()

    @abstractmethod
    def statistics(self) -> ThreatStatistics:
        raise NotImplementedError()
