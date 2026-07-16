from __future__ import annotations

import json
from datetime import datetime
from typing import Any, Dict, Iterable, Optional

from app.core.logger import get_logger
from app.repo.inmemory import InMemoryGraphRepo

from .models import (
    EntityDetails,
    EvidenceDetails,
    EvidenceQueryRequest,
    EvidenceSearchResult,
    EvidenceStatistics,
    EvidenceSummary,
    EvidenceTimeline,
    EvidenceTimelineEntry,
    RelationshipDetails,
    EvidenceValidation,
)
from .repository import EvidenceRepository

logger = get_logger("evidence_query_repository")


class InMemoryEvidenceRepository(EvidenceRepository):
    """Read model backed by the processed graph repository.

    This class only reads repository state. It never calls pipeline functions,
    writes nodes, or triggers Kafka processing.
    """

    def __init__(self, graph_repository: InMemoryGraphRepo):
        self._graph = graph_repository

    def _relationships(self) -> Iterable[Dict[str, Any]]:
        return self._graph.relationships

    def _is_evidence(self, node: Dict[str, Any]) -> bool:
        return "EVIDENCE" in [str(label).upper() for label in node.get("labels", [])]

    def _evidence(self, evidence_id: str, node: Dict[str, Any]) -> EvidenceDetails:
        properties = dict(node.get("properties", {}))
        related = []
        for relationship in self._relationships():
            if relationship.get("from") == evidence_id:
                related.append(relationship.get("to"))
            elif relationship.get("to") == evidence_id:
                related.append(relationship.get("from"))
        return EvidenceDetails(
            evidence_id=evidence_id,
            evidence_type=str(properties.get("evidence_type", properties.get("type", "unknown"))),
            source=str(properties.get("source", "unknown")),
            timestamp=self._timestamp(properties.get("timestamp")),
            confidence=float(properties.get("confidence", 0.0)),
            properties=properties,
            entity_ids=[item for item in related if item],
        )

    @staticmethod
    def _timestamp(value: Any) -> Optional[str]:
        if value is None:
            return None
        if isinstance(value, datetime):
            return value.isoformat()
        return str(value)

    @staticmethod
    def _in_time_range(item: EvidenceDetails, request: EvidenceQueryRequest) -> bool:
        if not request.start_time and not request.end_time:
            return True
        if not item.timestamp:
            return False
        try:
            timestamp = datetime.fromisoformat(item.timestamp.replace("Z", "+00:00"))
        except ValueError:
            return False
        if request.start_time and timestamp < request.start_time:
            return False
        if request.end_time and timestamp > request.end_time:
            return False
        return True

    def _all_evidence(self) -> list[EvidenceDetails]:
        return [self._evidence(node_id, node) for node_id, node in self._graph.nodes.items() if self._is_evidence(node)]

    def find_by_id(self, evidence_id: str) -> Optional[EvidenceDetails]:
        node = self._graph.nodes.get(evidence_id)
        if node is not None and self._is_evidence(node):
            return self._evidence(evidence_id, node)
        for item in self._all_evidence():
            if item.properties.get("event_id") == evidence_id:
                return item
        return None

    def find_entity(self, entity_id: str) -> Optional[EntityDetails]:
        node = self._graph.nodes.get(entity_id)
        if node is None or self._is_evidence(node):
            return None
        evidence_ids = []
        for evidence in self._all_evidence():
            if entity_id in evidence.entity_ids:
                evidence_ids.append(evidence.evidence_id)
        return EntityDetails(
            entity_id=entity_id,
            entity_type=(node.get("labels") or ["unknown"])[0].lower(),
            labels=list(node.get("labels", [])),
            attributes=dict(node.get("properties", {})),
            evidence_ids=evidence_ids,
        )

    def find_by_entity(self, entity_id: str) -> list[EvidenceDetails]:
        return [item for item in self._all_evidence() if entity_id in item.entity_ids]

    def find_relationships(self, evidence_id: str) -> list[RelationshipDetails]:
        relationships = []
        for relationship in self._relationships():
            if evidence_id in {relationship.get("from"), relationship.get("to")}:
                relationships.append(RelationshipDetails(
                    source_id=relationship["from"],
                    target_id=relationship["to"],
                    relationship_type=relationship["type"],
                    properties=dict(relationship.get("properties", {})),
                ))
        return relationships

    def find_timeline(self, request: EvidenceQueryRequest) -> EvidenceTimeline:
        result = self.search(request)
        return EvidenceTimeline(
            investigation_id=request.investigation_id,
            items=[EvidenceTimelineEntry(
                evidence_id=item.evidence_id,
                timestamp=item.timestamp,
                evidence_type=item.evidence_type,
                source=item.source,
                properties=item.properties,
            ) for item in result.items],
        )

    def find_metadata(self, evidence_id: str) -> Optional[EvidenceSummary]:
        item = self.find_by_id(evidence_id)
        if item is None:
            return None
        return EvidenceSummary(**item.model_dump(exclude={"properties", "entity_ids"}))

    def validate(self, evidence_id: str) -> Optional[EvidenceValidation]:
        item = self.find_by_id(evidence_id)
        if item is None:
            return None
        errors = []
        if not item.evidence_id:
            errors.append("evidence_id is required")
        if not item.source or item.source == "unknown":
            errors.append("source is not recorded")
        return EvidenceValidation(valid=not errors, errors=errors)

    def search(self, request: EvidenceQueryRequest) -> EvidenceSearchResult:
        items = self._all_evidence()
        if request.entity_id:
            items = [item for item in items if request.entity_id in item.entity_ids]
        if request.evidence_type:
            items = [item for item in items if item.evidence_type == request.evidence_type]
        if request.investigation_id:
            items = [item for item in items if item.properties.get("investigation_id") == request.investigation_id]
        if request.correlation_id:
            items = [item for item in items if item.properties.get("correlation_id") == request.correlation_id]
        items = [item for item in items if self._in_time_range(item, request)]
        if request.query:
            needle = request.query.lower()
            items = [item for item in items if needle in json.dumps(item.model_dump(mode="json"), default=str).lower()]
        total = len(items)
        page = items[request.offset:request.offset + request.limit]
        logger.info("evidence_query_search", extra={"total": total, "offset": request.offset, "limit": request.limit})
        return EvidenceSearchResult(items=page, total=total, offset=request.offset, limit=request.limit)

    def statistics(self) -> EvidenceStatistics:
        items = self._all_evidence()
        by_type: Dict[str, int] = {}
        by_source: Dict[str, int] = {}
        for item in items:
            by_type[item.evidence_type] = by_type.get(item.evidence_type, 0) + 1
            by_source[item.source] = by_source.get(item.source, 0) + 1
        return EvidenceStatistics(
            total_evidence=len(items),
            total_entities=len([node for node in self._graph.nodes.values() if not self._is_evidence(node)]),
            total_relationships=len(self._graph.relationships),
            by_type=by_type,
            by_source=by_source,
        )
