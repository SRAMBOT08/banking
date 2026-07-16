from __future__ import annotations

from typing import Any, Dict, List

from .interfaces import AITool, EvidenceTool, ExecutionTool, GraphTool, KnowledgeTool, MemoryTool, ThreatTool
from ..state import InvestigationState


class MockEvidenceTool(EvidenceTool):
    def name(self) -> str:
        return "evidence"

    def execute(self, state: InvestigationState, params: Dict[str, Any]) -> Dict[str, Any]:
        round_number = int(state.metadata.get("evidence_round", 0)) + 1
        return {"evidence": [{"id": f"evidence-{round_number}", "type": "authentication_event", "risk": "elevated", "round": round_number}]}


class MockKnowledgeTool(KnowledgeTool):
    def name(self) -> str:
        return "knowledge"

    def execute(self, state: InvestigationState, query: Dict[str, Any]) -> Dict[str, Any]:
        return {"patterns": [{"id": "pattern-account-takeover", "name": "Account Takeover", "description": "Suspicious account access sequence", "priority": 80}], "taxonomy_version": "mock-1"}


class MockThreatTool(ThreatTool):
    def name(self) -> str:
        return "threat"

    def execute(self, state: InvestigationState, candidates: List[Dict[str, Any]] | Dict[str, Any]) -> Any:
        if isinstance(candidates, dict) and candidates.get("missing_evidence_check"):
            return {"missing_evidence": []}
        if isinstance(candidates, dict) and ("graph" in candidates or "patterns" in candidates):
            return {"knowledge": 0.82, "pattern": 0.78, "graph": 0.71, "history": 0.62, "policy": 0.76, "ml": 0.0, "threat_feed": 0.0}
        return [{"id": "pattern-account-takeover", "name": "Account Takeover", "description": "Suspicious account access sequence", "priority": 80}]


class MockGraphTool(GraphTool):
    def name(self) -> str:
        return "graph"

    def execute(self, cypher: str, params: Dict[str, Any]) -> Dict[str, Any]:
        return {"connected_components": 1, "centrality": 0.71, "relationships": 3}


class MockMemoryTool(MemoryTool):
    def name(self) -> str:
        return "memory"

    def execute(self, state: InvestigationState, params: Dict[str, Any]) -> Dict[str, Any]:
        return {"historical_investigations": [{"id": "historical-1", "similarity": 0.62, "outcome": "reviewed"}]}


class MockAITool(AITool):
    def name(self) -> str:
        return "ai"

    def execute(self, state: InvestigationState, prompt: str) -> str:
        return f"Investigation {state.investigation_id} is ready for executive review."


class MockExecutionTool(ExecutionTool):
    def name(self) -> str:
        return "execution"

    def execute(self, state: InvestigationState, params: Dict[str, Any]) -> Dict[str, Any]:
        return {"status": "planned", "requires_policy_approval": True, "steps": ["review", "approve", "execute"]}


def mock_tool_set() -> Dict[str, Any]:
    return {"evidence": MockEvidenceTool(), "knowledge": MockKnowledgeTool(), "threat": MockThreatTool(), "graph": MockGraphTool(), "memory": MockMemoryTool(), "ai": MockAITool(), "execution": MockExecutionTool()}
