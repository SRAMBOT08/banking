from __future__ import annotations
from datetime import timedelta
from uuid import uuid5, NAMESPACE_URL
from ..models.case_execution import ApprovalRecord, ApprovalStatus, ExecutionPlan as CaseExecutionPlan, now_utc


class ApprovalManager:
    def create(self, plan: CaseExecutionPlan) -> tuple[ApprovalRecord, ...]:
        records = []
        for decision in plan.policy_decisions:
            if decision.requires_approval:
                records.append(ApprovalRecord(approval_id=uuid5(NAMESPACE_URL, f'{plan.execution_id}:{decision.policy_id}'), status=ApprovalStatus.PENDING, required_approvers=('manager',), expires_at=now_utc() + timedelta(hours=2)))
        return tuple(records)
    def approve(self, record: ApprovalRecord, approver: str, reason: str = '') -> ApprovalRecord:
        if record.status == ApprovalStatus.EXPIRED or (record.expires_at and record.expires_at <= now_utc()):
            return record.model_copy(update={'status': ApprovalStatus.EXPIRED})
        return record.model_copy(update={'status': ApprovalStatus.APPROVED, 'approved_by': (*record.approved_by, approver), 'history': (*record.history, {'approver': approver, 'reason': reason, 'at': now_utc()})})
