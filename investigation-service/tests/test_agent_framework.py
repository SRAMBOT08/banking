from __future__ import annotations

import pytest
from langgraph.types import Command

from app.agent.checkpoint_manager import CheckpointManager
from app.agent.confidence_manager import ConfidenceManager
from app.agent.decision_engine import DecisionAction, DecisionEngine
from app.agent.graph import GraphBuilder
from app.agent.hypothesis_manager import HypothesisManager
from app.agent.reasoning import ReasoningEngine
from app.agent.state import InvestigationState, WorkflowStatus
from app.agent.tool_router import ToolPolicy, ToolRouter
from app.agent.tools.mock_tools import mock_tool_set


def router() -> ToolRouter:
    return ToolRouter(mock_tool_set())


def test_state_guards_and_rollback():
    state = InvestigationState.new("i-state", "tenant")
    state.transition(WorkflowStatus.COLLECTING_EVIDENCE)
    with pytest.raises(ValueError):
        state.transition(WorkflowStatus.COMPLETED)
    state.transition(WorkflowStatus.ROLLED_BACK)
    state.transition(WorkflowStatus.COLLECTING_EVIDENCE)
    assert state.workflow_status is WorkflowStatus.COLLECTING_EVIDENCE
    assert state.state_durations_ms[WorkflowStatus.NEW.value] >= 0


def test_hypothesis_lifecycle_and_ranking():
    manager = HypothesisManager()
    first = manager.create("A", "first", priority=2)
    second = manager.create("B", "second", priority=1)
    first = manager.update(first, confidence=0.6)
    second = manager.update(second, confidence=0.9)
    assert manager.rank([first, second])[0]["id"] == second["id"]
    merged = manager.merge(first, second)
    assert len(merged["relationships"]) == 1
    assert manager.restore(manager.archive(manager.reject(merged, "insufficient")))["status"] == "active"


def test_confidence_breakdown():
    result = ConfidenceManager().breakdown({"knowledge": 1.0, "pattern": 0.5, "graph": 0.5})
    assert result["final"] == pytest.approx(2 / 3)
    assert "knowledge" in result


def test_decision_engine_is_deterministic():
    state = InvestigationState.new("i-decision", "tenant")
    state.final_confidence = 0.9
    assert DecisionEngine().decide(state)["action"] == DecisionAction.REQUIRE_HUMAN_APPROVAL.value
    state.missing_evidence = [{"type": "device"}]
    assert DecisionEngine().decide(state)["action"] == DecisionAction.COLLECT_ADDITIONAL_EVIDENCE.value


def test_checkpoint_recovery():
    manager = CheckpointManager()
    state = InvestigationState.new("i-checkpoint", "tenant")
    state.transition(WorkflowStatus.COLLECTING_EVIDENCE)
    checkpoint_id = manager.create_checkpoint(state, "test")
    state.metadata["changed"] = True
    restored = manager.resume(checkpoint_id)
    assert restored.metadata.get("changed") is None
    assert manager.metadata(checkpoint_id)["status"] == "resumed"


def test_mock_workflow_completes():
    graph = GraphBuilder(router()).build()
    state = InvestigationState.new("i-complete", "tenant")
    result = graph.invoke({"state": state.model_dump(mode="json")}, config={"configurable": {"thread_id": "i-complete"}})
    completed = InvestigationState.model_validate(result["state"])
    assert completed.workflow_status is WorkflowStatus.COMPLETED
    assert completed.ai_summary
    assert completed.execution_plan["status"] == "planned"
    assert completed.tool_outputs["decision"]["action"] == DecisionAction.EXECUTION_ALLOWED.value


def test_mock_workflow_pauses_and_resumes_for_approval():
    graph = GraphBuilder(router()).build()
    state = InvestigationState.new("i-approval", "tenant")
    state.metadata["human_approval_required"] = True
    config = {"configurable": {"thread_id": "i-approval"}}
    paused = graph.invoke({"state": state.model_dump(mode="json")}, config=config)
    assert paused.get("__interrupt__")
    resumed = graph.invoke(Command(resume="approved"), config=config)
    assert InvestigationState.model_validate(resumed["state"]).workflow_status is WorkflowStatus.COMPLETED


def test_router_retry_and_discovery():
    class Flaky:
        def __init__(self):
            self.calls = 0
        def name(self):
            return "flaky"
        def execute(self):
            self.calls += 1
            if self.calls == 1:
                raise RuntimeError("transient")
            return "ok"

    tool = Flaky()
    router_instance = ToolRouter({"flaky": tool}, {"flaky": ToolPolicy(max_retries=1)})
    assert router_instance.invoke("flaky") == "ok"
    assert router_instance.discover("f") == ["flaky"]
    assert len(router_instance.execution_history) == 2
