from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional


class KnowledgeRegistryRepository(ABC):
    @abstractmethod
    def load(self, source: str) -> None:
        pass

    @abstractmethod
    def reload(self) -> None:
        pass

    @abstractmethod
    def get_attack_pattern(self, name: str, version: Optional[str] = None) -> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    def list_patterns(self) -> Dict[str, Dict[str, Any]]:
        pass

    @abstractmethod
    def get_indicator(self, indicator_id: str) -> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    def list_indicators(self) -> List[Dict[str, Any]]:
        pass
