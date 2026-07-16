from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, Dict, List
from ..state import InvestigationState


class Tool(ABC):
    @abstractmethod
    def name(self) -> str:
        raise NotImplementedError()


class EvidenceTool(Tool, ABC):
    @abstractmethod
    def execute(self, state: InvestigationState, params: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError()


class KnowledgeTool(Tool, ABC):
    @abstractmethod
    def execute(self, state: InvestigationState, query: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError()


class ThreatTool(Tool, ABC):
    @abstractmethod
    def execute(self, state: InvestigationState, candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        raise NotImplementedError()


class GraphTool(Tool, ABC):
    @abstractmethod
    def execute(self, cypher: str, params: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError()


class MemoryTool(Tool, ABC):
    @abstractmethod
    def execute(self, state: InvestigationState, params: Dict[str, Any]) -> Any:
        raise NotImplementedError()


class AITool(Tool, ABC):
    @abstractmethod
    def execute(self, state: InvestigationState, prompt: str) -> str:
        raise NotImplementedError()


class ExecutionTool(Tool, ABC):
    @abstractmethod
    def execute(self, state: InvestigationState, params: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError()
