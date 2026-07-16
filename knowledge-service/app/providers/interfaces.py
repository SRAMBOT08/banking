from __future__ import annotations
from typing import Iterable, Protocol
from app.query.models import KnowledgeDetails, KnowledgeRecommendation, KnowledgeRelationship


class KnowledgeProvider(Protocol):
    name: str
    def items(self) -> Iterable[KnowledgeDetails]: ...
    def recommendations(self) -> Iterable[KnowledgeRecommendation]: ...
    def relationships(self) -> Iterable[KnowledgeRelationship]: ...


class ProviderRegistry:
    def __init__(self, providers: Iterable[KnowledgeProvider] = ()):
        self._providers = {provider.name: provider for provider in providers}

    def register(self, provider: KnowledgeProvider) -> None:
        self._providers[provider.name] = provider

    def providers(self) -> tuple[KnowledgeProvider, ...]:
        return tuple(self._providers.values())

    def get(self, name: str) -> KnowledgeProvider:
        return self._providers[name]
