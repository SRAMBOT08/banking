from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional


class AttackGraphRepository(ABC):
    @abstractmethod
    def load_patterns(self, patterns: Dict[str, Dict]):
        pass

    @abstractmethod
    def get_pattern(self, name: str) -> Optional[Dict]:
        pass

    @abstractmethod
    def get_node(self, node_id: str) -> Optional[Dict]:
        pass

    @abstractmethod
    def find_by_mitre(self, technique: str) -> List[Dict]:
        pass

    @abstractmethod
    def traverse(self, start_nodes: List[str], depth: int = 3) -> Dict:
        pass
