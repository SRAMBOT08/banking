from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List


class GraphRepository(ABC):
    @abstractmethod
    def create_node(self, canonical_id: str, labels: List[str], properties: Dict[str, Any]):
        pass

    @abstractmethod
    def merge_node(self, canonical_id: str, labels: List[str], properties: Dict[str, Any]):
        pass

    @abstractmethod
    def create_relationship(self, from_id: str, to_id: str, rel_type: str, properties: Dict[str, Any]):
        pass

    @abstractmethod
    def merge_relationship(self, from_id: str, to_id: str, rel_type: str, properties: Dict[str, Any]):
        pass

    @abstractmethod
    def fetch_entity(self, canonical_id: str) -> Optional[Dict[str, Any]]:
        pass
