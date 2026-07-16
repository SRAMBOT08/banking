from __future__ import annotations
from typing import Any, Callable, Dict, Optional, TypedDict
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import interrupt
from .checkpoint_manager import CheckpointManager
from .reasoning import ReasoningEngine
from .decision_engine import DecisionEngine
from .state import InvestigationState
from .tool_router import ToolRouter
from .nodes import aggregate_confidence, build_investigation, collect_evidence, decision_engine, execution_planning, generate_ai_report, generate_hypotheses, graph_analysis, human_approval, identify_missing_evidence, retrieve_history, retrieve_knowledge, run_pattern_matching


class GraphState(TypedDict):
    state: Dict[str, Any]


class GraphBuilder:
    def __init__(self, router: ToolRouter, reasoning: Optional[ReasoningEngine] = None, decision: Optional[DecisionEngine] = None, checkpoints: Optional[CheckpointManager] = None):
        self.router, self.reasoning, self.decision, self.checkpoints = router, reasoning or ReasoningEngine(), decision or DecisionEngine(), checkpoints or CheckpointManager()
        self._nodes: Dict[str, Callable] = {}

    def register_node(self, name: str, handler: Callable) -> None:
        if name in self._nodes:
            raise ValueError(f"Node already registered: {name}")
        self._nodes[name] = handler

    def build(self):
        graph = StateGraph(GraphState)
        def wrap(handler: Callable) -> Callable:
            def invoke(graph_state: GraphState) -> GraphState:
                model = InvestigationState.model_validate(graph_state["state"])
                updated = handler(model)
                return {"state": updated.model_dump(mode="json")}
            return invoke
        handlers = {
            "collect_evidence": lambda s: collect_evidence(s, self.router), "retrieve_knowledge": lambda s: retrieve_knowledge(s, self.router),
            "run_pattern_matching": lambda s: run_pattern_matching(s, self.router), "identify_missing_evidence": lambda s: identify_missing_evidence(s, self.router),
            "graph_analysis": lambda s: graph_analysis(s, self.router), "retrieve_history": lambda s: retrieve_history(s, self.router),
            "generate_hypotheses": lambda s: generate_hypotheses(s, self.router), "aggregate_confidence": lambda s: aggregate_confidence(s, self.router), "decision_engine": lambda s: decision_engine(s, self.router, {"engine": self.decision}),
            "checkpoint": self._checkpoint, "human_approval": self._approval, "build_investigation": lambda s: build_investigation(s, self.router),
            "generate_ai_report": lambda s: generate_ai_report(s, self.router), "execution_planning": lambda s: execution_planning(s, self.router),
        }
        for name, handler in {**self._nodes, **handlers}.items():
            graph.add_node(name, wrap(handler))
        graph.add_edge(START, "collect_evidence")
        graph.add_edge("collect_evidence", "retrieve_knowledge")
        graph.add_edge("retrieve_knowledge", "run_pattern_matching")
        graph.add_edge("run_pattern_matching", "identify_missing_evidence")
        graph.add_conditional_edges("identify_missing_evidence", self._evidence_route, {"collect_more": "collect_evidence", "continue": "graph_analysis"})
        graph.add_edge("graph_analysis", "retrieve_history")
        graph.add_edge("retrieve_history", "generate_hypotheses")
        graph.add_edge("generate_hypotheses", "aggregate_confidence")
        graph.add_edge("aggregate_confidence", "decision_engine")
        graph.add_conditional_edges("decision_engine", self._decision_route, {"approval": "checkpoint", "more_evidence": "collect_evidence", "continue": "build_investigation"})
        graph.add_edge("checkpoint", "human_approval")
        graph.add_conditional_edges("human_approval", self._approval_result_route, {"resume": "build_investigation", "wait": "human_approval"})
        graph.add_edge("build_investigation", "generate_ai_report")
        graph.add_edge("generate_ai_report", "execution_planning")
        graph.add_edge("execution_planning", END)
        return graph.compile(checkpointer=MemorySaver())

    def _checkpoint(self, state: InvestigationState) -> InvestigationState:
        self.checkpoints.create_checkpoint(state, "human_approval")
        return state

    def _approval(self, state: InvestigationState) -> InvestigationState:
        decision = state.metadata.get("approval_decision")
        if decision is None:
            decision = interrupt({"type": "human_approval", "investigation_id": state.investigation_id, "checkpoint_id": state.checkpoint_id})
        state.metadata["approval_decision"] = decision or "approved"
        return human_approval(state, self.router, {"decision": state.metadata["approval_decision"]})

    def _evidence_route(self, graph_state: GraphState) -> str:
        state = InvestigationState.model_validate(graph_state["state"])
        return "collect_more" if self.reasoning.needs_more_evidence(state) else "continue"

    def _approval_route(self, graph_state: GraphState) -> str:
        state = InvestigationState.model_validate(graph_state["state"])
        return "approval" if self.reasoning.requires_approval(state) else "continue"

    @staticmethod
    def _decision_route(graph_state: GraphState) -> str:
        from .decision_engine import DecisionEngine
        state = InvestigationState.model_validate(graph_state["state"])
        return DecisionEngine.route(state.metadata.get("decision", {}))

    @staticmethod
    def _approval_result_route(graph_state: GraphState) -> str:
        state = InvestigationState.model_validate(graph_state["state"])
        return "resume" if state.metadata.get("approval_decision") in {"approved", "rejected"} else "wait"
