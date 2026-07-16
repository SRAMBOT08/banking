from __future__ import annotations

import logging
from typing import Optional

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
from .repository import ThreatRepository

logger = logging.getLogger("sentineliq.threat.query")


class ThreatQueryService:
    """Read application service for processed Threat Intelligence."""

    def __init__(self, repository: ThreatRepository):
        self._repository = repository

    def find_pattern(self, pattern: str, version: Optional[str] = None) -> Optional[ThreatPattern]:
        logger.info({"event": "threat_query", "operation": "find_pattern", "pattern": pattern, "version": version})
        return self._repository.find_pattern(pattern, version)

    def find_indicator(self, indicator: str) -> Optional[ThreatIndicator]:
        logger.info({"event": "threat_query", "operation": "find_indicator", "indicator": indicator})
        return self._repository.find_indicator(indicator)

    def find_threat(self, threat_id: str) -> Optional[ThreatDetails]:
        logger.info({"event": "threat_query", "operation": "find_threat", "threat_id": threat_id})
        return self._repository.find_threat(threat_id)

    def find_attack(self, attack: str, version: Optional[str] = None) -> Optional[ThreatPattern]:
        return self._repository.find_attack(attack, version)

    def metadata(self) -> ThreatMetadata:
        return self._repository.find_metadata()

    def validate(self) -> ThreatValidation:
        return self._repository.validate()

    def search(self, request: ThreatSearchRequest) -> ThreatSearchResult:
        return self._repository.search(request)

    def statistics(self) -> ThreatStatistics:
        return self._repository.statistics()
