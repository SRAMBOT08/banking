from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Iterable, List, Optional
import json


class RegistryProvider(ABC):
    @abstractmethod
    def load(self) -> Iterable[Any]:
        raise NotImplementedError

    def list(self) -> List[Any]:
        return list(self.load())


class StaticProvider(RegistryProvider):
    def __init__(self, items: Optional[Iterable[Any]] = None):
        self._items = list(items or [])

    def load(self) -> Iterable[Any]:
        return tuple(self._items)

    def replace(self, items: Iterable[Any]) -> None:
        self._items = list(items)

    def get(self, identifier: str, field: str = "id") -> Any:
        return next((item for item in self._items if (item.get(field) if isinstance(item, dict) else getattr(item, field, None)) == identifier), None)

    def search(self, query: str) -> List[Any]:
        query = query.casefold().strip()
        if not query:
            return self.list()
        def text(item: Any) -> str:
            return json.dumps(item, sort_keys=True, default=str) if isinstance(item, dict) else item.model_dump_json()
        return [item for item in self._items if query in text(item).casefold()]


class AttackPatternProvider(StaticProvider):
    pass


class MitreProvider(StaticProvider):
    pass


class FraudProvider(StaticProvider):
    pass


class IndicatorProvider(StaticProvider):
    pass


class RecommendationProvider(StaticProvider):
    pass


class ConfidenceProvider(StaticProvider):
    pass


class RelationshipProvider(StaticProvider):
    pass


class ProviderManager:
    """Coordinates static providers and prevents provider details leaking outward."""

    def __init__(self, providers: Optional[dict[str, StaticProvider]] = None):
        self.providers = providers or {
            "attack_patterns": AttackPatternProvider(),
            "mitre": MitreProvider(),
            "fraud": FraudProvider(),
            "indicators": IndicatorProvider(),
            "recommendations": RecommendationProvider(),
            "confidence": ConfidenceProvider(),
            "relationships": RelationshipProvider(),
        }

    def replace(self, domain: str, items: Iterable[Any]) -> None:
        self.providers[domain].replace(items)

    def list(self, domain: str) -> List[Any]:
        return self.providers[domain].list()

    def get(self, domain: str, identifier: str, field: str = "id") -> Any:
        return self.providers[domain].get(identifier, field)

    def search(self, domain: str, query: str) -> List[Any]:
        return self.providers[domain].search(query)

    def count(self) -> int:
        return len(self.providers)
