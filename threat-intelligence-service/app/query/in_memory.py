from __future__ import annotations

import json
from typing import Any, Dict, Optional

from app.core.logger import get_logger
from app.knowledge_registry.manager import RegistryManager
from app.repositories.candidates_repo import InMemoryCandidatesRepo

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

logger = get_logger("threat_query_repository")


class InMemoryThreatRepository(ThreatRepository):
    """Read-only facade over processed candidates and the loaded registry snapshot."""

    def __init__(self, registry: RegistryManager, candidates: InMemoryCandidatesRepo):
        self._registry = registry
        self._candidates = candidates

    @staticmethod
    def _pattern(pattern: Any) -> ThreatPattern:
        data = pattern.model_dump(mode="json") if hasattr(pattern, "model_dump") else dict(pattern)
        return ThreatPattern.model_validate(data)

    @staticmethod
    def _indicator(indicator: Any) -> ThreatIndicator:
        data = indicator.model_dump(mode="json") if hasattr(indicator, "model_dump") else dict(indicator)
        return ThreatIndicator.model_validate(data)

    @staticmethod
    def _candidate(candidate: Any) -> ThreatDetails:
        data = candidate.model_dump(mode="json") if hasattr(candidate, "model_dump") else dict(candidate)
        explanation = dict(data.get("explanation") or {})
        missing = explanation.get("missing_evidence", explanation.get("missing", []))
        return ThreatDetails(
            threat_id=str(data.get("candidate_id", data.get("threat_id", ""))),
            pattern_name=str(data.get("pattern_name", "unknown")),
            pattern_version=str(data.get("pattern_version", "1.0")),
            confidence=float(data.get("confidence", 0)),
            tenant_id=data.get("tenant_id"),
            investigation_id=data.get("investigation_id"),
            correlation_id=data.get("correlation_id"),
            timestamp=data.get("timestamp"),
            explanation=explanation,
            evidence_refs=list(data.get("evidence_refs") or []),
            missing_evidence=list(missing or []),
            metadata={"version": data.get("version", "1.0")},
        )

    def _all_threats(self) -> list[ThreatDetails]:
        return [self._candidate(item) for item in self._candidates.list_all()]

    def find_pattern(self, pattern: str, version: Optional[str] = None) -> Optional[ThreatPattern]:
        item = self._registry.get_attack_pattern(pattern, version)
        return self._pattern(item) if item is not None else None

    def find_indicator(self, indicator: str) -> Optional[ThreatIndicator]:
        item = self._registry.get_indicator(indicator)
        return self._indicator(item) if item is not None else None

    def find_threat(self, threat_id: str) -> Optional[ThreatDetails]:
        return next((item for item in self._all_threats() if item.threat_id == threat_id), None)

    def find_attack(self, attack: str, version: Optional[str] = None) -> Optional[ThreatPattern]:
        return self.find_pattern(attack, version)

    def find_metadata(self) -> ThreatMetadata:
        stats = self._registry.get_registry_statistics()
        return ThreatMetadata(
            registry_version=stats.registry_version,
            validation_status=stats.validation_status,
            pattern_count=stats.pattern_count,
            indicator_count=stats.indicator_count,
            candidate_count=len(self._candidates.list_all()),
        )

    def validate(self) -> ThreatValidation:
        result = self._registry.validate_registry()
        findings = list(result.get("findings", []))
        return ThreatValidation(
            valid=bool(result.get("valid", False)),
            errors=[finding for finding in findings if finding.get("severity") == "critical"],
            warnings=[finding for finding in findings if finding.get("severity") != "critical"],
        )

    def search(self, request: ThreatSearchRequest) -> ThreatSearchResult:
        items = self._all_threats()
        if request.investigation_id:
            items = [item for item in items if item.investigation_id == request.investigation_id]
        if request.tenant_id:
            items = [item for item in items if item.tenant_id == request.tenant_id]
        if request.correlation_id:
            items = [item for item in items if item.correlation_id == request.correlation_id]
        if request.pattern_name:
            items = [item for item in items if item.pattern_name == request.pattern_name]
        if request.min_confidence is not None:
            items = [item for item in items if item.confidence >= request.min_confidence]
        if request.query:
            query = request.query.casefold()
            items = [item for item in items if query in json.dumps(item.model_dump(mode="json"), default=str).casefold()]
        total = len(items)
        page = items[request.offset:request.offset + request.limit]
        logger.info("threat_query_search", extra={"total": total, "offset": request.offset, "limit": request.limit})
        return ThreatSearchResult(items=page, total=total, offset=request.offset, limit=request.limit)

    def statistics(self) -> ThreatStatistics:
        stats = self._registry.get_registry_statistics()
        threats = self._all_threats()
        return ThreatStatistics(
            pattern_count=stats.pattern_count,
            indicator_count=stats.indicator_count,
            threat_count=len(threats),
            high_confidence_count=len([item for item in threats if item.confidence >= 70]),
            registry_version=stats.registry_version,
            validation_status=stats.validation_status,
        )
