from __future__ import annotations
import hashlib, json
from uuid import UUID
from ..adapter import ExecutionAdapter
from ..approval import ApprovalManager
from ..models import CaseExecutionPlan, CaseFileInput, ExecutionStatus, ExecutionStatusView, PolicyOutcome
from ..models.case_execution import ApprovalStatus
from ..planner import CaseExecutionPlanner
from ..policy import CasePolicyEngine
from ..repository import CaseExecutionRepository


class CaseExecutionService:
    def __init__(self, repository: CaseExecutionRepository, adapter: ExecutionAdapter | None = None):
        self.repository, self.adapter = repository, adapter
        self.planner, self.policy, self.approvals = CaseExecutionPlanner(), CasePolicyEngine(), ApprovalManager()
    def create(self, payload: dict, created_by='system') -> CaseExecutionPlan:
        case = CaseFileInput.model_validate(payload)
        source_hash = hashlib.sha256(json.dumps(payload, sort_keys=True, default=str).encode()).hexdigest()
        execution_id = CaseExecutionPlan.stable_id(case.case_id, case.case_version)
        plan = self.planner.build(case, execution_id=execution_id, created_by=created_by, source_hash=source_hash)
        decisions = tuple(self.policy.evaluate(case, action) for action in plan.actions)
        approvals = self.approvals.create(plan.model_copy(update={'policy_decisions': decisions}))
        if any(item.outcome == PolicyOutcome.DENIED for item in decisions): status = ExecutionStatus.DENIED
        elif any(item.outcome == PolicyOutcome.DEFERRED for item in decisions): status = ExecutionStatus.DEFERRED
        elif approvals: status = ExecutionStatus.WAITING_APPROVAL
        else: status = ExecutionStatus.APPROVED
        plan = plan.model_copy(update={'policy_decisions': decisions, 'approvals': approvals, 'status': status})
        stored = self.repository.create(plan)
        self.repository.add_audit(plan.execution_id, plan.case_id, plan.correlation_id, 'EXECUTION_PLANNED', created_by, {'policy_decision': status.value, 'actions': len(plan.actions)})
        return stored
    def get(self, execution_id: UUID): return self.repository.get(execution_id)
    def approve(self, execution_id: UUID, approver: str, reason: str = '') -> CaseExecutionPlan:
        plan = self.get(execution_id)
        if plan.status != ExecutionStatus.WAITING_APPROVAL: raise ValueError('execution is not waiting for approval')
        approvals = tuple(self.approvals.approve(record, approver, reason) for record in plan.approvals)
        if any(record.status == ApprovalStatus.EXPIRED for record in approvals): raise ValueError('approval has expired')
        updated = plan.model_copy(update={'approvals': approvals, 'status': ExecutionStatus.APPROVED})
        stored = self.repository.update(updated)
        self.repository.add_audit(plan.execution_id, plan.case_id, plan.correlation_id, 'EXECUTION_APPROVED', approver, {'reason': reason})
        return stored
    def status(self, execution_id: UUID) -> ExecutionStatusView:
        plan = self.get(execution_id); policy = plan.policy_decisions[0].outcome if plan.policy_decisions else PolicyOutcome.DEFERRED; approval = plan.approvals[0].status if plan.approvals else ApprovalStatus.NOT_REQUIRED
        return ExecutionStatusView(execution_id=plan.execution_id, status=plan.status, action_statuses={str(a.action_id): a.status for a in plan.actions}, policy_decision=policy, approval_status=approval)
    async def execute(self, execution_id: UUID, actor='system'):
        plan = self.get(execution_id)
        if plan.status != ExecutionStatus.APPROVED: raise ValueError('execution requires an approved plan')
        if self.adapter is None: raise ValueError('execution adapter is not configured')
        results = []
        for action in plan.actions:
            if not self.adapter.supports(action.operation): raise ValueError(f'unsupported operation: {action.operation}')
            result = await self.adapter.execute(str(plan.execution_id), action); results.append(result)
            self.repository.add_audit(plan.execution_id, plan.case_id, plan.correlation_id, 'ACTION_EXECUTED', actor, {'action_id': str(action.action_id), 'service_now_ticket': result.get('response', {}).get('result', {}).get('number') if isinstance(result.get('response'), dict) else None})
        return results
