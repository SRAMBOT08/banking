from __future__ import annotations
from datetime import datetime, timezone
from enum import StrEnum
from typing import Any
from uuid import UUID, uuid5, NAMESPACE_URL
from pydantic import BaseModel, ConfigDict, Field


class FrozenModel(BaseModel):
    model_config = ConfigDict(frozen=True, extra='forbid')


class PolicyOutcome(StrEnum):
    ALLOWED = 'ALLOWED'
    DENIED = 'DENIED'
    REQUIRES_APPROVAL = 'REQUIRES_APPROVAL'
    DEFERRED = 'DEFERRED'


class ApprovalStatus(StrEnum):
    NOT_REQUIRED = 'NOT_REQUIRED'
    PENDING = 'PENDING'
    APPROVED = 'APPROVED'
    DENIED = 'DENIED'
    EXPIRED = 'EXPIRED'


class ExecutionStatus(StrEnum):
    PLANNED = 'PLANNED'
    WAITING_APPROVAL = 'WAITING_APPROVAL'
    APPROVED = 'APPROVED'
    RUNNING = 'RUNNING'
    COMPLETED = 'COMPLETED'
    FAILED = 'FAILED'
    DEFERRED = 'DEFERRED'
    DENIED = 'DENIED'


class AdapterOperation(StrEnum):
    CREATE_INCIDENT = 'CREATE_INCIDENT'
    UPDATE_INCIDENT = 'UPDATE_INCIDENT'
    ADD_WORK_NOTE = 'ADD_WORK_NOTE'
    ASSIGN_GROUP = 'ASSIGN_GROUP'
    CLOSE_INCIDENT = 'CLOSE_INCIDENT'
    RETRIEVE_STATUS = 'RETRIEVE_STATUS'


class CaseFileInput(FrozenModel):
    model_config = ConfigDict(frozen=True, extra='allow')
    case_id: UUID
    metadata: dict[str, Any]
    recommendations: dict[str, Any] = Field(default_factory=dict)
    decision: dict[str, Any] = Field(default_factory=dict)
    execution: dict[str, Any] = Field(default_factory=dict)
    evidence: dict[str, Any] = Field(default_factory=dict)
    threat: dict[str, Any] = Field(default_factory=dict)
    audit: dict[str, Any] = Field(default_factory=dict)
    version: dict[str, Any]

    @property
    def investigation_id(self) -> str: return str(self.metadata['investigation_id'])
    @property
    def tenant_id(self) -> str: return str(self.metadata['tenant_id'])
    @property
    def correlation_id(self) -> str: return str(self.metadata['correlation_id'])
    @property
    def case_version(self) -> int: return int(self.version.get('version', 1))


class PolicyDecision(FrozenModel):
    policy_id: str
    outcome: PolicyOutcome
    reason: str
    rules: tuple[str, ...] = ()
    requires_approval: bool = False


class ApprovalRecord(FrozenModel):
    approval_id: UUID
    status: ApprovalStatus
    required_approvers: tuple[str, ...] = ()
    approved_by: tuple[str, ...] = ()
    history: tuple[dict[str, Any], ...] = ()
    expires_at: datetime | None = None


class ExecutionAction(FrozenModel):
    action_id: UUID
    recommendation_id: str
    operation: AdapterOperation
    title: str
    description: str
    priority: int = Field(default=0, ge=0, le=100)
    order: int = Field(ge=1)
    dependencies: tuple[UUID, ...] = ()
    payload: dict[str, Any] = Field(default_factory=dict)
    rollback_strategy: str = 'manual_review'
    status: ExecutionStatus = ExecutionStatus.PLANNED


class ExecutionPlan(FrozenModel):
    execution_id: UUID
    case_id: UUID
    case_version: int
    investigation_id: str
    tenant_id: str
    correlation_id: str
    actions: tuple[ExecutionAction, ...]
    policy_decisions: tuple[PolicyDecision, ...]
    approvals: tuple[ApprovalRecord, ...]
    status: ExecutionStatus
    rollback_strategy: str
    created_at: datetime
    created_by: str
    source_hash: str

    @staticmethod
    def stable_id(case_id: UUID, case_version: int) -> UUID:
        return uuid5(NAMESPACE_URL, f'sentineliq:execution:{case_id}:{case_version}')


class AuditRecord(FrozenModel):
    audit_id: UUID
    execution_id: UUID
    case_id: UUID
    correlation_id: str
    event_type: str
    occurred_at: datetime
    actor: str
    details: dict[str, Any] = Field(default_factory=dict)
    previous_hash: str = ''
    record_hash: str


class ExecutionStatusView(FrozenModel):
    execution_id: UUID
    status: ExecutionStatus
    action_statuses: dict[str, ExecutionStatus]
    policy_decision: PolicyOutcome
    approval_status: ApprovalStatus


def now_utc() -> datetime: return datetime.now(timezone.utc)
