from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, Dict, List
from ..state import InvestigationState


class Tool(ABC):
    """Base interface for all Tools wrapping platform microservices."""

    @abstractmethod
    def name(self) -> str:
        raise NotImplementedError()


class EvidenceTool(Tool, ABC):
    @abstractmethod
    def collect(self, state: InvestigationState, params: Dict[str, Any]) -> InvestigationState:
        """Collect evidence and append to the state's evidence list."""
        raise NotImplementedError()


class KnowledgeTool(Tool, ABC):
    @abstractmethod
    def query(self, state: InvestigationState, query: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError()


class ThreatTool(Tool, ABC):
    @abstractmethod
    def match_patterns(self, state: InvestigationState, candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        raise NotImplementedError()


class GraphTool(Tool, ABC):
    @abstractmethod
    def run_query(self, cypher: str, params: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError()


class MemoryTool(Tool, ABC):
    @abstractmethod
    def retrieve(self, investigation_id: str) -> InvestigationState:
        raise NotImplementedError()


class InvestigationTool(Tool, ABC):
    @abstractmethod
    def persist(self, state: InvestigationState) -> None:
        raise NotImplementedError()


class AIServiceTool(Tool, ABC):
    @abstractmethod
    def generate_report(self, state: InvestigationState, prompt: str) -> str:
        raise NotImplementedError()


class ExecutionTool(Tool, ABC):
    @abstractmethod
    def plan(self, state: InvestigationState) -> Dict[str, Any]:
        raise NotImplementedError()
