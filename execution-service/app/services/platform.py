from __future__ import annotations

from datetime import datetime, timezone
from typing import Dict, List

from app.config.settings import Settings
from app.models import (
    ApprovalDecision,
    ApprovalStatus,
    ExecutionCategory,
    ExecutionPlan,
    ExecutionResult,
    ExecutionState,
    ExecutionStatistics,
    ExecutionTask,
    ExecutionTaskState,
)
from app.policies import (
    CompositeExecutionPolicyEngine,
    DeterministicApprovalPolicy,
    DeterministicRetryPolicy,
    DeterministicRollbackPolicy,
    RiskPolicy,
    SchedulingWindowPolicy,
    TenantPolicy,
    is_blocked,
    requires_approval,
)
from app.queue.engine import DeterministicExecutionQueueEngine
from app.repositories.inmemory import ExecutionRepository
from app.services.audit import ExecutionAuditEngine
from app.services.planner import ExecutionPlanner
from app.services.verification import ExecutionVerificationEngine


class ExecutionPlatformService:
    def __init__(self, settings: Settings, repository: ExecutionRepository):
        self.settings = settings
        self.repository = repository
        self.planner = ExecutionPlanner()
        self.audit_engine = ExecutionAuditEngine()
        self.verification_engine = ExecutionVerificationEngine()
        self.queue_engine = DeterministicExecutionQueueEngine()
        self.policy_engine = CompositeExecutionPolicyEngine(
            [RiskPolicy(settings), TenantPolicy(), SchedulingWindowPolicy(settings)]
        )
        self.approval_policy = DeterministicApprovalPolicy(settings)
        self.retry_policy = DeterministicRetryPolicy()
        self.rollback_policy = DeterministicRollbackPolicy()

    def create_plan(self, payload: Dict) -> tuple[ExecutionPlan, list, list]:
        plan = self.planner.build(payload)
        plan.plan_state = ExecutionState.POLICY_EVALUATED

        all_policy_decisions = []
        approval_decisions: List[ApprovalDecision] = []

        for task in plan.tasks:
            task.state = ExecutionTaskState.WAITING_POLICY
            decisions = self.policy_engine.evaluate(plan, task)
            all_policy_decisions.extend(decisions)

            if is_blocked(decisions):
                task.state = ExecutionTaskState.FAILED
            elif requires_approval(decisions):
                task.state = ExecutionTaskState.WAITING_APPROVAL
                approval = self.approval_policy.evaluate(plan, task)
                approval_decisions.append(approval)
                if approval.status == ApprovalStatus.AUTO_APPROVED:
                    task.state = ExecutionTaskState.APPROVED
                else:
                    task.state = ExecutionTaskState.WAITING_APPROVAL
            else:
                task.state = ExecutionTaskState.APPROVED

            if task.state == ExecutionTaskState.APPROVED:
                task.state = ExecutionTaskState.READY

        queue = self.queue_engine.build_queue(plan.plan_id, plan.tasks)
        self.queue_engine.refresh_ready(queue, {task.task_id: task for task in plan.tasks})
        self.repository.upsert_queue(queue)

        plan.plan_state = ExecutionState.READY if queue.ready_tasks else ExecutionState.WAITING_APPROVAL

        self.repository.save_plan(plan)
        self.repository.add_policy_decisions(plan.plan_id, all_policy_decisions)
        for approval in approval_decisions:
            self.repository.add_approval_decision(plan.plan_id, approval)

        self._audit(plan, None, "PLAN_CREATED", "execution plan created", {"tasks": len(plan.tasks)})
        return plan, all_policy_decisions, approval_decisions

    def approve_task(self, task_id: str, approver: str, reason: str):
        task = self._require_task(task_id)
        task.state = ExecutionTaskState.APPROVED
        task.updated_at = datetime.now(timezone.utc).isoformat()
        self.repository.update_task(task)
        self._audit_by_task(task, "TASK_APPROVED", reason, {"approver": approver})
        return task

    def cancel_task(self, task_id: str, reason: str):
        task = self._require_task(task_id)
        task.state = ExecutionTaskState.CANCELLED
        task.updated_at = datetime.now(timezone.utc).isoformat()
        self.repository.update_task(task)
        self._audit_by_task(task, "TASK_CANCELLED", reason, {})
        return task

    def retry_task(self, task_id: str, reason: str):
        task = self._require_task(task_id)
        if not self.retry_policy.should_retry(task):
            raise ValueError("retry policy denied")
        task.retry_count += 1
        task.state = ExecutionTaskState.READY
        task.updated_at = datetime.now(timezone.utc).isoformat()
        self.repository.update_task(task)
        self._audit_by_task(task, "TASK_RETRY", reason, {"retry_count": task.retry_count})
        return task

    def patch_task(self, task_id: str, *, state: str | None = None, expected_result: dict | None = None,
                   observed_result: dict | None = None, error: str | None = None):
        task = self._require_task(task_id)
        if state:
            task.state = ExecutionTaskState(state)
        task.updated_at = datetime.now(timezone.utc).isoformat()
        self.repository.update_task(task)

        verification = None
        if task.state in {ExecutionTaskState.VERIFYING, ExecutionTaskState.COMPLETED, ExecutionTaskState.FAILED}:
            result = ExecutionResult(
                correlation_id=task.correlation_id,
                investigation_id=task.investigation_id,
                tenant_id=task.tenant_id,
                plan_id=self._plan_id_for_task(task_id),
                task_id=task.task_id,
                state=task.state,
                expected_result=expected_result or {},
                observed_result=observed_result or {},
                error=error,
            )
            verification = self.verification_engine.verify(result)
            self.repository.add_verification(self._plan_id_for_task(task_id), verification)

        if task.state == ExecutionTaskState.FAILED and self.rollback_policy.should_rollback(task):
            task.state = ExecutionTaskState.ROLLED_BACK
            self.repository.update_task(task)

        self._audit_by_task(task, "TASK_PATCHED", "task updated", {"state": task.state.value})
        return task, verification

    def replay_plan(self, plan_id: str):
        tasks = self.repository.list_tasks(plan_id)
        tasks = sorted(tasks, key=lambda item: (item.deterministic_order, item.task_id))
        for task in tasks:
            if task.state in {ExecutionTaskState.READY, ExecutionTaskState.QUEUED}:
                task.state = ExecutionTaskState.RUNNING
                self.repository.update_task(task)
                task.state = ExecutionTaskState.COMPLETED
                self.repository.update_task(task)
        self.repository.append_history(plan_id, {"action": "REPLAY", "timestamp": datetime.now(timezone.utc).isoformat()})
        return self.repository.list_tasks(plan_id)

    def statistics(self) -> ExecutionStatistics:
        tasks = self.repository.list_tasks()
        by_state: Dict[str, int] = {}
        by_category: Dict[str, int] = {}
        for task in tasks:
            by_state[task.state.value] = by_state.get(task.state.value, 0) + 1
            by_category[task.category.value] = by_category.get(task.category.value, 0) + 1
        queue_depth = sum(len((self.repository.get_queue(plan.plan_id).pending_tasks if self.repository.get_queue(plan.plan_id) else [])) for plan in self.repository.list_plans())
        return ExecutionStatistics(
            plan_count=len(self.repository.list_plans()),
            task_count=len(tasks),
            queue_depth=queue_depth,
            by_state=by_state,
            by_category=by_category,
        )

    def _require_task(self, task_id: str) -> ExecutionTask:
        task = self.repository.get_task(task_id)
        if task is None:
            raise KeyError(task_id)
        return task

    def _plan_id_for_task(self, task_id: str) -> str:
        for plan in self.repository.list_plans():
            if any(task.task_id == task_id for task in plan.tasks):
                return plan.plan_id
        raise KeyError(task_id)

    def _audit(self, plan: ExecutionPlan, task_id: str | None, event_type: str, reason: str, details: dict):
        record = self.audit_engine.record(
            correlation_id=plan.correlation_id,
            investigation_id=plan.investigation_id,
            tenant_id=plan.tenant_id,
            plan_id=plan.plan_id,
            task_id=task_id,
            event_type=event_type,
            reason=reason,
            details=details,
        )
        self.repository.add_audit(record)

    def _audit_by_task(self, task: ExecutionTask, event_type: str, reason: str, details: dict):
        plan_id = self._plan_id_for_task(task.task_id)
        plan = self.repository.get_plan(plan_id)
        assert plan is not None
        self._audit(plan, task.task_id, event_type, reason, details)
