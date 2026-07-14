from __future__ import annotations

from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import uuid4

from pydantic import BaseModel, Field



def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class ExecutionTaskState(str, Enum):
    CREATED = "CREATED"
    PLANNED = "PLANNED"
    WAITING_POLICY = "WAITING_POLICY"
    POLICY_APPROVED = "POLICY_APPROVED"
    WAITING_APPROVAL = "WAITING_APPROVAL"
    APPROVED = "APPROVED"
    READY = "READY"
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    VERIFYING = "VERIFYING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
    ROLLED_BACK = "ROLLED_BACK"


class ExecutionCategory(str, Enum):
    SOC = "SOC"
    FRAUD = "FRAUD"
    COMPLIANCE = "COMPLIANCE"
    RISK = "RISK"
    SECURITY = "SECURITY"
    OPERATIONS = "OPERATIONS"
    UNSUPPORTED = "UNSUPPORTED"


class PolicyStatus(str, Enum):
    ALLOWED = "ALLOWED"
    DENIED = "DENIED"
    APPROVAL_REQUIRED = "APPROVAL_REQUIRED"
    BLOCKED = "BLOCKED"
    EXPIRED = "EXPIRED"
    UNSUPPORTED = "UNSUPPORTED"


class ApprovalStatus(str, Enum):
    AUTO_APPROVED = "AUTO_APPROVED"
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    DENIED = "DENIED"
    EXPIRED = "EXPIRED"
    ESCALATED = "ESCALATED"


class VerificationStatus(str, Enum):
    VERIFIED = "VERIFIED"
    MISMATCH = "MISMATCH"
    INSUFFICIENT = "INSUFFICIENT"


class ExecutionState(str, Enum):
    CREATED = "CREATED"
    POLICY_EVALUATED = "POLICY_EVALUATED"
    WAITING_APPROVAL = "WAITING_APPROVAL"
    READY = "READY"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
    VERIFIED = "VERIFIED"


class BaseExecutionModel(BaseModel):
    model_version: str = "1.0"
    created_at: str = Field(default_factory=utc_now)
    updated_at: str = Field(default_factory=utc_now)
    correlation_id: str
    investigation_id: str
    tenant_id: str


class ExecutionDependency(BaseModel):
    dependency_id: str = Field(default_factory=lambda: str(uuid4()))
    task_id: str
    depends_on_task_id: str
    dependency_type: str = "FINISH_TO_START"


class ExecutionTask(BaseExecutionModel):
    task_id: str = Field(default_factory=lambda: str(uuid4()))
    snapshot_version: int
    recommendation_id: str
    task_title: str
    task_description: str
    category: ExecutionCategory
    priority: int = Field(ge=0, le=100)
    deterministic_order: int
    state: ExecutionTaskState = ExecutionTaskState.CREATED
    dependencies: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    idempotency_key: str
    retry_count: int = 0
    max_retries: int = 3
    scheduled_for: Optional[str] = None


class ExecutionPlan(BaseExecutionModel):
    plan_id: str = Field(default_factory=lambda: str(uuid4()))
    snapshot_id: str
    snapshot_version: int
    risk_score: int = Field(ge=0, le=100)
    confidence_score: int = Field(ge=0, le=100)
    policy_results: Dict[str, Any] = Field(default_factory=dict)
    plan_state: ExecutionState = ExecutionState.CREATED
    tasks: List[ExecutionTask] = Field(default_factory=list)
    dependencies: List[ExecutionDependency] = Field(default_factory=list)
    context: Dict[str, Any] = Field(default_factory=dict)


class PolicyDecision(BaseExecutionModel):
    decision_id: str = Field(default_factory=lambda: str(uuid4()))
    plan_id: str
    task_id: str
    status: PolicyStatus
    explanation: str
    blocking_reason: Optional[str] = None
    policy_name: str
    violations: List[str] = Field(default_factory=list)


class ApprovalDecision(BaseExecutionModel):
    approval_id: str = Field(default_factory=lambda: str(uuid4()))
    plan_id: str
    task_id: str
    status: ApprovalStatus
    required_approvers: List[str] = Field(default_factory=list)
    approved_by: List[str] = Field(default_factory=list)
    approval_history: List[Dict[str, Any]] = Field(default_factory=list)
    expires_at: str = Field(default_factory=lambda: (datetime.now(timezone.utc) + timedelta(minutes=120)).isoformat())
    explanation: str = ""


class ExecutionResult(BaseExecutionModel):
    result_id: str = Field(default_factory=lambda: str(uuid4()))
    plan_id: str
    task_id: str
    state: ExecutionTaskState
    expected_result: Dict[str, Any] = Field(default_factory=dict)
    observed_result: Dict[str, Any] = Field(default_factory=dict)
    error: Optional[str] = None


class ExecutionVerification(BaseExecutionModel):
    verification_id: str = Field(default_factory=lambda: str(uuid4()))
    plan_id: str
    task_id: str
    verification_status: VerificationStatus
    mismatch_details: List[str] = Field(default_factory=list)
    verified_at: str = Field(default_factory=utc_now)


class ExecutionTimeline(BaseModel):
    entries: List[Dict[str, Any]] = Field(default_factory=list)


class ExecutionHistory(BaseModel):
    items: List[Dict[str, Any]] = Field(default_factory=list)


class ExecutionAuditRecord(BaseExecutionModel):
    audit_id: str = Field(default_factory=lambda: str(uuid4()))
    plan_id: str
    task_id: Optional[str] = None
    operator: str = "system"
    reason: str
    event_type: str
    details: Dict[str, Any] = Field(default_factory=dict)


class ExecutionQueue(BaseExecutionModel):
    queue_id: str = Field(default_factory=lambda: str(uuid4()))
    plan_id: str
    pending_tasks: List[str] = Field(default_factory=list)
    ready_tasks: List[str] = Field(default_factory=list)
    blocked_tasks: List[str] = Field(default_factory=list)
    waiting_tasks: List[str] = Field(default_factory=list)
    retry_queue: List[str] = Field(default_factory=list)
    cancelled_tasks: List[str] = Field(default_factory=list)
    completed_tasks: List[str] = Field(default_factory=list)
    failed_tasks: List[str] = Field(default_factory=list)
    dead_letter_queue: List[str] = Field(default_factory=list)


class ExecutionMetrics(BaseModel):
    requests: int = 0
    plans_created: int = 0
    tasks_total: int = 0
    tasks_completed: int = 0
    tasks_failed: int = 0
    tasks_cancelled: int = 0
    policy_denied: int = 0
    policy_approval_required: int = 0
    approvals_pending: int = 0
    verifications_mismatch: int = 0


class ExecutionStatistics(BaseModel):
    plan_count: int = 0
    task_count: int = 0
    queue_depth: int = 0
    by_state: Dict[str, int] = Field(default_factory=dict)
    by_category: Dict[str, int] = Field(default_factory=dict)
