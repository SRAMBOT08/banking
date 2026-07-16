from __future__ import annotations
import json
from collections import Counter
from typing import Iterable, List, Optional, Type, TypeVar
from app.providers import BuiltinEnterpriseProvider, KnowledgeProvider, ProviderRegistry
from .models import *
from .repository import KnowledgeRepository


ModelT = TypeVar("ModelT", bound=KnowledgeDetails)


class InMemoryKnowledgeRepository(KnowledgeRepository):
    """Read-only repository facade over provider snapshots."""

    def __init__(self, providers: ProviderRegistry | None = None, *, registry_version: str = "1.0"):
        self._providers = providers or ProviderRegistry([BuiltinEnterpriseProvider()])
        self._registry_version = registry_version
        self._items: dict[str, KnowledgeDetails] = {}
        self._recommendations: dict[str, KnowledgeRecommendation] = {}
        self._relationships: dict[str, KnowledgeRelationship] = {}
        self._refresh()

    def _refresh(self) -> None:
        self._items = {}
        self._recommendations = {}
        self._relationships = {}
        for provider in self._providers.providers():
            self._items.update({item.id: item for item in provider.items()})
            self._recommendations.update({item.id: item for item in provider.recommendations()})
            self._relationships.update({item.id: item for item in provider.relationships()})

    def _typed(self, item_id: str, model: Type[ModelT]) -> Optional[ModelT]:
        item = self._items.get(item_id)
        return model.model_validate(item.model_dump(mode="json")) if item else None

    def find_item(self, item_id: str):
        return self._items.get(item_id)

    def find_pattern(self, item_id: str):
        item = self._items.get(item_id)
        if not item or item.category not in {KnowledgeCategory.GENERIC, KnowledgeCategory.FRAUD}:
            return None
        return AttackPattern.model_validate(item.model_dump(mode="json"))

    def find_technique(self, item_id: str): return self._typed(item_id, MITRETechnique)
    def find_tactic(self, item_id: str): return self._typed(item_id, MITRETactic)
    def find_control(self, item_id: str): return self._typed(item_id, SecurityControl)
    def find_playbook(self, item_id: str): return self._typed(item_id, Playbook)
    def find_fraud_pattern(self, item_id: str): return self._typed(item_id, FraudPattern)
    def find_detection_rule(self, item_id: str): return self._typed(item_id, DetectionRule)
    def find_indicator(self, item_id: str): return self._typed(item_id, ThreatIndicator)
    def find_quantum_pattern(self, item_id: str): return self._typed(item_id, QuantumThreatPattern)
    def find_recommendation(self, item_id: str): return self._recommendations.get(item_id)
    def find_relationship(self, relationship_id: str): return self._relationships.get(relationship_id)

    def relationships(self, item_id: str) -> List[KnowledgeRelationship]:
        return [item for item in self._relationships.values() if item.source_id == item_id or item.target_id == item_id]

    def search(self, request: KnowledgeSearchRequest) -> KnowledgeSearchResponse:
        items = list(self._items.values())
        if request.category: items = [item for item in items if item.category == request.category]
        if request.provider: items = [item for item in items if item.provider == request.provider]
        if request.version: items = [item for item in items if item.version == request.version or any(version.version == request.version for version in item.versions)]
        if request.tags:
            wanted = {tag.casefold() for tag in request.tags}
            items = [item for item in items if wanted.intersection({tag.name.casefold() for tag in item.tags})]
        if not request.include_deprecated: items = [item for item in items if not item.deprecated]
        if request.query:
            query = request.query.casefold()
            items = [item for item in items if query in json.dumps(item.model_dump(mode="json"), default=str).casefold()]
        if request.relationship_type:
            ids = {rel.source_id for rel in self._relationships.values() if rel.relationship_type == request.relationship_type} | {rel.target_id for rel in self._relationships.values() if rel.relationship_type == request.relationship_type}
            items = [item for item in items if item.id in ids]
        total = len(items)
        page = items[request.offset:request.offset + request.limit]
        return KnowledgeSearchResponse(items=page, total=total, offset=request.offset, limit=request.limit, metadata=self.metadata())

    def metadata(self):
        stats = self.statistics()
        return KnowledgeMetadata(platform_version="1.0", registry_version=self._registry_version, provider_count=len(self._providers.providers()), item_count=stats.item_count, relationship_count=stats.relationship_count, categories=stats.by_category)

    def statistics(self):
        categories = Counter(item.category.value for item in self._items.values())
        return KnowledgeStatistics(item_count=len(self._items), relationship_count=len(self._relationships), provider_count=len(self._providers.providers()), by_category=dict(categories), deprecated_count=sum(item.deprecated for item in self._items.values()), current_version=self._registry_version)

    def validate(self):
        errors = []
        for item in self._items.values():
            if not item.id or not item.name: errors.append(f"invalid knowledge item: {item.id}")
        for relation in self._relationships.values():
            if relation.source_id not in self._items and relation.source_id not in self._recommendations: errors.append(f"relationship source not found: {relation.source_id}")
            if relation.target_id not in self._items and relation.target_id not in self._recommendations: errors.append(f"relationship target not found: {relation.target_id}")
        return KnowledgeValidation(valid=not errors, errors=errors)

    def versions(self, item_id: str):
        item = self._items.get(item_id)
        if not item: return []
        return [PatternVersion(id=f"{item.id}:{version.version}", item_id=item.id, version=version, snapshot=item if version.status == "current" else None) for version in item.versions] or [PatternVersion(id=f"{item.id}:{item.version}", item_id=item.id, version=KnowledgeVersion(version=item.version, status="current"), snapshot=item)]

    def similar(self, item_id: str, limit: int = 10):
        item = self._items.get(item_id)
        if not item: return []
        tag_names = {tag.name for tag in item.tags}
        candidates = [candidate for candidate in self._items.values() if candidate.id != item_id and tag_names.intersection({tag.name for tag in candidate.tags})]
        return candidates[:limit]
