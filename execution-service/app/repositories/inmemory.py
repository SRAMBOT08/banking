from __future__ import annotations

from threading import RLock
from typing import Dict, List, Optional

from app.models import (
    ApprovalDecision,
    ExecutionAuditRecord,
    ExecutionHistory,
    ExecutionMetrics,
    ExecutionPlan,
    ExecutionQueue,
    ExecutionTask,
    ExecutionTimeline,
    ExecutionVerification,
    PolicyDecision,
)


class ExecutionRepository:
    def __init__(self):
        self._plans: Dict[str, ExecutionPlan] = {}
        self._tasks: Dict[str, ExecutionTask] = {}
        self._plan_tasks: Dict[str, List[str]] = {}
        self._policy_decisions: Dict[str, List[PolicyDecision]] = {}
        self._approval_decisions: Dict[str, List[ApprovalDecision]] = {}
        self._verifications: Dict[str, List[ExecutionVerification]] = {}
        self._audit: List[ExecutionAuditRecord] = []
        self._history: Dict[str, ExecutionHistory] = {}
        self._timeline: Dict[str, ExecutionTimeline] = {}
        self._queues: Dict[str, ExecutionQueue] = {}
        self._metrics = ExecutionMetrics()
        self._lock = RLock()

    def save_plan(self, plan: ExecutionPlan) -> None:
        with self._lock:
            self._plans[plan.plan_id] = plan
            self._plan_tasks[plan.plan_id] = [task.task_id for task in plan.tasks]
            for task in plan.tasks:
                self._tasks[task.task_id] = task
            self._history.setdefault(plan.plan_id, ExecutionHistory())
            self._timeline.setdefault(plan.plan_id, ExecutionTimeline())
            self._metrics.plans_created += 1
            self._metrics.tasks_total += len(plan.tasks)

    def list_plans(self) -> List[ExecutionPlan]:
        return sorted(self._plans.values(), key=lambda item: (item.investigation_id, item.plan_id))

    def get_plan(self, plan_id: str) -> Optional[ExecutionPlan]:
        return self._plans.get(plan_id)

    def list_tasks(self, plan_id: str | None = None) -> List[ExecutionTask]:
        if plan_id is None:
            return sorted(self._tasks.values(), key=lambda item: (item.investigation_id, item.deterministic_order, item.task_id))
        return [self._tasks[task_id] for task_id in self._plan_tasks.get(plan_id, [])]

    def get_task(self, task_id: str) -> Optional[ExecutionTask]:
        return self._tasks.get(task_id)

    def update_task(self, task: ExecutionTask) -> None:
        with self._lock:
            self._tasks[task.task_id] = task

    def add_policy_decisions(self, plan_id: str, decisions: List[PolicyDecision]) -> None:
        with self._lock:
            self._policy_decisions.setdefault(plan_id, []).extend(decisions)
            self._metrics.policy_denied += sum(dec.status.name == "DENIED" for dec in decisions)
            self._metrics.policy_approval_required += sum(dec.status.name == "APPROVAL_REQUIRED" for dec in decisions)

    def add_approval_decision(self, plan_id: str, decision: ApprovalDecision) -> None:
        with self._lock:
            self._approval_decisions.setdefault(plan_id, []).append(decision)
            if decision.status.name == "PENDING":
                self._metrics.approvals_pending += 1

    def add_verification(self, plan_id: str, verification: ExecutionVerification) -> None:
        with self._lock:
            self._verifications.setdefault(plan_id, []).append(verification)
            if verification.verification_status.name == "MISMATCH":
                self._metrics.verifications_mismatch += 1

    def add_audit(self, record: ExecutionAuditRecord) -> None:
        with self._lock:
            self._audit.append(record)

    def list_audit(self) -> List[ExecutionAuditRecord]:
        return list(self._audit)

    def append_history(self, plan_id: str, item: dict) -> None:
        with self._lock:
            self._history.setdefault(plan_id, ExecutionHistory()).items.append(item)

    def append_timeline(self, plan_id: str, item: dict) -> None:
        with self._lock:
            self._timeline.setdefault(plan_id, ExecutionTimeline()).entries.append(item)

    def get_history(self, plan_id: str | None = None) -> dict:
        if plan_id:
            return {"plan_id": plan_id, "items": self._history.get(plan_id, ExecutionHistory()).items}
        return {"items": {pid: history.items for pid, history in self._history.items()}}

    def metrics(self) -> ExecutionMetrics:
        self._metrics.requests += 1
        self._metrics.tasks_completed = sum(task.state.name == "COMPLETED" for task in self._tasks.values())
        self._metrics.tasks_failed = sum(task.state.name == "FAILED" for task in self._tasks.values())
        self._metrics.tasks_cancelled = sum(task.state.name == "CANCELLED" for task in self._tasks.values())
        return self._metrics

    def upsert_queue(self, queue: ExecutionQueue) -> None:
        self._queues[queue.plan_id] = queue

    def get_queue(self, plan_id: str) -> Optional[ExecutionQueue]:
        return self._queues.get(plan_id)
