from __future__ import annotations
from copy import deepcopy
from datetime import datetime, timezone
from enum import Enum
from typing import Any, ClassVar, Dict, List, Optional
from uuid import uuid4
from pydantic import BaseModel, Field


class WorkflowStatus(str, Enum):
    NEW = "NEW"
    COLLECTING_EVIDENCE = "COLLECTING_EVIDENCE"
    KNOWLEDGE_RETRIEVAL = "KNOWLEDGE_RETRIEVAL"
    PATTERN_MATCHING = "PATTERN_MATCHING"
    GRAPH_ANALYSIS = "GRAPH_ANALYSIS"
    HISTORY_ANALYSIS = "HISTORY_ANALYSIS"
    HYPOTHESIS_GENERATION = "HYPOTHESIS_GENERATION"
    CONFIDENCE_AGGREGATION = "CONFIDENCE_AGGREGATION"
    DECISION_ENGINE = "DECISION_ENGINE"
    WAITING_FOR_APPROVAL = "WAITING_FOR_APPROVAL"
    REPORT_GENERATION = "REPORT_GENERATION"
    EXECUTION_PLANNING = "EXECUTION_PLANNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    ROLLED_BACK = "ROLLED_BACK"
    CANCELLED = "CANCELLED"


class NodeExecution(BaseModel):
    node: str
    started_at: datetime
    finished_at: Optional[datetime] = None
    duration_ms: Optional[float] = None
    previous_node: Optional[str] = None
    status: str = "started"
    retry_count: int = 0
    failure_count: int = 0
    checkpoint_id: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    error: Optional[str] = None

    def finish(self, status: str = "completed", error: Optional[str] = None) -> None:
        self.finished_at = datetime.now(timezone.utc)
        self.duration_ms = (self.finished_at - self.started_at).total_seconds() * 1000
        self.status = status
        self.error = error


class InvestigationState(BaseModel):
    investigation_id: str
    tenant_id: str
    workflow_status: WorkflowStatus = WorkflowStatus.NEW
    current_node: Optional[str] = None
    previous_node: Optional[str] = None
    history: List[Dict[str, Any]] = Field(default_factory=list)
    evidence: List[Dict[str, Any]] = Field(default_factory=list)
    knowledge: Dict[str, Any] = Field(default_factory=dict)
    graph_results: Dict[str, Any] = Field(default_factory=dict)
    intelligence_context: Dict[str, Any] = Field(default_factory=dict)
    matched_patterns: List[Dict[str, Any]] = Field(default_factory=list)
    candidate_patterns: List[Dict[str, Any]] = Field(default_factory=list)
    hypotheses: List[Dict[str, Any]] = Field(default_factory=list)
    selected_hypothesis: Optional[Dict[str, Any]] = None
    confidence_breakdown: Dict[str, float] = Field(default_factory=dict)
    final_confidence: Optional[float] = None
    missing_evidence: List[Dict[str, Any]] = Field(default_factory=list)
    recommendations: List[Dict[str, Any]] = Field(default_factory=list)
    execution_plan: Dict[str, Any] = Field(default_factory=dict)
    ai_summary: Optional[str] = None
    tool_outputs: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    node_executions: List[NodeExecution] = Field(default_factory=list)
    retry_count: int = 0
    failure_count: int = 0
    retry_history: List[Dict[str, Any]] = Field(default_factory=list)
    checkpoint_id: Optional[str] = None
    checkpoint_history: List[str] = Field(default_factory=list)
    timestamps: Dict[str, datetime] = Field(default_factory=dict)
    state_durations_ms: Dict[str, float] = Field(default_factory=dict)
    execution_metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    ALLOWED_TRANSITIONS: ClassVar[Dict[WorkflowStatus, set[WorkflowStatus]]] = {
        WorkflowStatus.NEW: {WorkflowStatus.COLLECTING_EVIDENCE, WorkflowStatus.CANCELLED},
        WorkflowStatus.COLLECTING_EVIDENCE: {WorkflowStatus.KNOWLEDGE_RETRIEVAL, WorkflowStatus.PATTERN_MATCHING, WorkflowStatus.FAILED, WorkflowStatus.ROLLED_BACK, WorkflowStatus.CANCELLED},
        WorkflowStatus.KNOWLEDGE_RETRIEVAL: {WorkflowStatus.PATTERN_MATCHING, WorkflowStatus.FAILED, WorkflowStatus.ROLLED_BACK, WorkflowStatus.CANCELLED},
        WorkflowStatus.PATTERN_MATCHING: {WorkflowStatus.COLLECTING_EVIDENCE, WorkflowStatus.GRAPH_ANALYSIS, WorkflowStatus.FAILED, WorkflowStatus.ROLLED_BACK, WorkflowStatus.CANCELLED},
        WorkflowStatus.GRAPH_ANALYSIS: {WorkflowStatus.HISTORY_ANALYSIS, WorkflowStatus.FAILED, WorkflowStatus.ROLLED_BACK, WorkflowStatus.CANCELLED},
        WorkflowStatus.HISTORY_ANALYSIS: {WorkflowStatus.HYPOTHESIS_GENERATION, WorkflowStatus.FAILED, WorkflowStatus.ROLLED_BACK, WorkflowStatus.CANCELLED},
        WorkflowStatus.HYPOTHESIS_GENERATION: {WorkflowStatus.CONFIDENCE_AGGREGATION, WorkflowStatus.FAILED, WorkflowStatus.ROLLED_BACK, WorkflowStatus.CANCELLED},
        WorkflowStatus.CONFIDENCE_AGGREGATION: {WorkflowStatus.DECISION_ENGINE, WorkflowStatus.FAILED, WorkflowStatus.ROLLED_BACK, WorkflowStatus.CANCELLED},
        WorkflowStatus.DECISION_ENGINE: {WorkflowStatus.WAITING_FOR_APPROVAL, WorkflowStatus.REPORT_GENERATION, WorkflowStatus.COLLECTING_EVIDENCE, WorkflowStatus.FAILED, WorkflowStatus.ROLLED_BACK, WorkflowStatus.CANCELLED},
        WorkflowStatus.WAITING_FOR_APPROVAL: {WorkflowStatus.REPORT_GENERATION, WorkflowStatus.ROLLED_BACK, WorkflowStatus.CANCELLED, WorkflowStatus.FAILED},
        WorkflowStatus.REPORT_GENERATION: {WorkflowStatus.EXECUTION_PLANNING, WorkflowStatus.FAILED, WorkflowStatus.ROLLED_BACK, WorkflowStatus.CANCELLED},
        WorkflowStatus.EXECUTION_PLANNING: {WorkflowStatus.COMPLETED, WorkflowStatus.FAILED, WorkflowStatus.ROLLED_BACK, WorkflowStatus.CANCELLED},
        WorkflowStatus.FAILED: {WorkflowStatus.ROLLED_BACK, WorkflowStatus.CANCELLED},
        WorkflowStatus.ROLLED_BACK: {WorkflowStatus.COLLECTING_EVIDENCE, WorkflowStatus.CANCELLED},
        WorkflowStatus.COMPLETED: set(), WorkflowStatus.CANCELLED: set(),
    }

    def transition(self, target: WorkflowStatus, node: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None) -> None:
        if target == self.workflow_status:
            return
        if target not in self.ALLOWED_TRANSITIONS.get(self.workflow_status, set()):
            raise ValueError(f"Illegal workflow transition: {self.workflow_status.value} -> {target.value}")
        source, now = self.workflow_status, datetime.now(timezone.utc)
        self.timestamps[f"{source.value}:exited"] = now
        entered = self.timestamps.get(f"{source.value}:entered")
        if entered:
            self.state_durations_ms[source.value] = (now - entered).total_seconds() * 1000
        self.workflow_status = target
        self.timestamps[f"{target.value}:entered"] = now
        self.previous_node, self.current_node = self.current_node, node or self.current_node
        self.add_history({"event": "state_transition", "from": source.value, "to": target.value, "node": node, "metadata": metadata or {}})

    def begin_node(self, node: str, metadata: Optional[Dict[str, Any]] = None) -> NodeExecution:
        execution = NodeExecution(node=node, started_at=datetime.now(timezone.utc), previous_node=self.current_node, metadata=metadata or {})
        self.previous_node, self.current_node = self.current_node, node
        self.node_executions.append(execution)
        self.add_history({"event": "node_start", "node": node, "previous_node": execution.previous_node})
        return execution

    def finish_node(self, execution: NodeExecution, status: str = "completed", error: Optional[str] = None) -> None:
        execution.finish(status, error)
        if status == "failed":
            self.failure_count += 1
        self.add_history({"event": "node_finish", "node": execution.node, "status": status, "duration_ms": execution.duration_ms, "error": error})

    def record_retry(self, reason: str, node: Optional[str] = None) -> None:
        self.retry_count += 1
        self.retry_history.append({"retry": self.retry_count, "node": node or self.current_node, "reason": reason, "timestamp": datetime.now(timezone.utc).isoformat()})
        self.add_history({"event": "retry", "node": node or self.current_node, "retry_count": self.retry_count, "reason": reason})

    def add_checkpoint(self, checkpoint_id: str) -> None:
        self.checkpoint_id = checkpoint_id
        self.checkpoint_history.append(checkpoint_id)
        self.add_history({"event": "checkpoint_created", "checkpoint_id": checkpoint_id})

    def add_history(self, entry: Dict[str, Any]) -> None:
        self.history.append({**entry, "timestamp": datetime.now(timezone.utc).isoformat()})
        self.updated_at = datetime.now(timezone.utc)

    def snapshot(self) -> "InvestigationState":
        data = self.model_dump() if hasattr(self, "model_dump") else self.dict()
        return InvestigationState.model_validate(deepcopy(data))

    @classmethod
    def new(cls, investigation_id: str, tenant_id: str) -> "InvestigationState":
        state = cls(investigation_id=investigation_id, tenant_id=tenant_id)
        state.timestamps[f"{WorkflowStatus.NEW.value}:entered"] = datetime.now(timezone.utc)
        return state

    def update_execution_metadata(self) -> None:
        """Update execution_metadata with current progress and performance metrics"""
        completed_nodes = len([e for e in self.node_executions if e.status == "completed"])
        failed_nodes = len([e for e in self.node_executions if e.status == "failed"])
        total_nodes = len(self.node_executions)
        total_duration = sum((e.duration_ms or 0) for e in self.node_executions if e.duration_ms)
        
        progress_percent = int((completed_nodes / total_nodes * 100)) if total_nodes > 0 else 0
        
        self.execution_metadata = {
            "progress_percent": progress_percent,
            "total_duration_ms": total_duration,
            "current_node": self.current_node,
            "completed_nodes": completed_nodes,
            "pending_nodes": total_nodes - completed_nodes - failed_nodes,
            "failed_nodes": failed_nodes,
            "total_nodes": total_nodes,
            "retry_count": self.retry_count,
            "failure_count": self.failure_count,
            "latest_error": self.node_executions[-1].error if self.node_executions and self.node_executions[-1].error else None,
            "checkpoint_id": self.checkpoint_id,
            "workflow_status": self.workflow_status.value,
            "confidence": float(self.final_confidence) if self.final_confidence else None,
            "evidence_count": len(self.evidence),
            "hypotheses_count": len(self.hypotheses),
            "last_updated": datetime.now(timezone.utc).isoformat(),
        }
        self.metadata["progress_percent"] = progress_percent

    def get_progress_percent(self) -> int:
        """Calculate progress as percentage of nodes completed"""
        if not self.node_executions:
            return 0
        completed = len([e for e in self.node_executions if e.status == "completed"])
        total = len(self.node_executions)
        return int((completed / total * 100)) if total > 0 else 0

    def get_node_durations(self) -> Dict[str, float]:
        """Get execution duration for each node in milliseconds"""
        return {e.node: e.duration_ms or 0 for e in self.node_executions}

    def get_completed_nodes(self) -> List[str]:
        """Get list of successfully completed node names"""
        return [e.node for e in self.node_executions if e.status == "completed"]

    def get_failed_nodes(self) -> List[str]:
        """Get list of failed node names"""
        return [e.node for e in self.node_executions if e.status == "failed"]

    def get_pending_nodes(self) -> List[str]:
        """Get list of nodes not yet started"""
        executed = {e.node for e in self.node_executions}
        # List of all expected nodes in typical workflow
        all_nodes = [
            "collect_evidence", "retrieve_knowledge", "run_pattern_matching",
            "identify_missing_evidence", "graph_analysis", "retrieve_history",
            "generate_hypotheses", "aggregate_confidence", "decision_engine",
            "checkpoint", "human_approval", "build_investigation",
            "generate_ai_report", "execution_planning"
        ]
        return [n for n in all_nodes if n not in executed]

    @staticmethod
    def new_checkpoint_id() -> str:
        return f"cp-{uuid4().hex}"
