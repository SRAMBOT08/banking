from __future__ import annotations

from datetime import datetime, timezone
from typing import List

from app.config.settings import Settings
from app.models import ExecutionPlan, ExecutionTask, PolicyDecision, PolicyStatus
from app.policies.base import ExecutionPolicy


class RiskPolicy(ExecutionPolicy):
    name = "risk_policy"

    def __init__(self, settings: Settings):
        self.settings = settings

    def evaluate(self, plan: ExecutionPlan, task: ExecutionTask) -> PolicyDecision:
        if plan.risk_score >= self.settings.risk_hard_block_threshold:
            status = PolicyStatus.BLOCKED
            explanation = "Risk threshold exceeded"
            blocking_reason = "RISK_HARD_BLOCK"
            violations = ["risk_score_above_hard_block_threshold"]
        elif plan.risk_score > self.settings.risk_auto_approve_threshold:
            status = PolicyStatus.APPROVAL_REQUIRED
            explanation = "Risk requires human approval"
            blocking_reason = None
            violations = ["risk_requires_approval"]
        else:
            status = PolicyStatus.ALLOWED
            explanation = "Risk policy allows execution"
            blocking_reason = None
            violations = []
        return PolicyDecision(
            correlation_id=plan.correlation_id,
            investigation_id=plan.investigation_id,
            tenant_id=plan.tenant_id,
            plan_id=plan.plan_id,
            task_id=task.task_id,
            status=status,
            explanation=explanation,
            blocking_reason=blocking_reason,
            policy_name=self.name,
            violations=violations,
        )


class SchedulingWindowPolicy(ExecutionPolicy):
    name = "scheduling_policy"

    def __init__(self, settings: Settings):
        self.settings = settings

    def evaluate(self, plan: ExecutionPlan, task: ExecutionTask) -> PolicyDecision:
        current_hour = datetime.now(timezone.utc).hour
        in_window = self.settings.execution_window_start_hour_utc <= current_hour <= self.settings.execution_window_end_hour_utc
        status = PolicyStatus.ALLOWED if in_window else PolicyStatus.BLOCKED
        return PolicyDecision(
            correlation_id=plan.correlation_id,
            investigation_id=plan.investigation_id,
            tenant_id=plan.tenant_id,
            plan_id=plan.plan_id,
            task_id=task.task_id,
            status=status,
            explanation="Execution window valid" if in_window else "Execution outside allowed UTC window",
            blocking_reason=None if in_window else "EXECUTION_WINDOW",
            policy_name=self.name,
            violations=[] if in_window else ["outside_execution_window"],
        )


class TenantPolicy(ExecutionPolicy):
    name = "tenant_policy"

    def evaluate(self, plan: ExecutionPlan, task: ExecutionTask) -> PolicyDecision:
        status = PolicyStatus.ALLOWED if plan.tenant_id else PolicyStatus.DENIED
        return PolicyDecision(
            correlation_id=plan.correlation_id,
            investigation_id=plan.investigation_id,
            tenant_id=plan.tenant_id,
            plan_id=plan.plan_id,
            task_id=task.task_id,
            status=status,
            explanation="Tenant isolation verified" if status == PolicyStatus.ALLOWED else "Tenant id missing",
            blocking_reason=None if status == PolicyStatus.ALLOWED else "TENANT_ID_REQUIRED",
            policy_name=self.name,
            violations=[] if status == PolicyStatus.ALLOWED else ["tenant_missing"],
        )


class CompositeExecutionPolicyEngine:
    def __init__(self, policies: List[ExecutionPolicy]):
        self.policies = policies

    def evaluate(self, plan: ExecutionPlan, task: ExecutionTask) -> List[PolicyDecision]:
        return [policy.evaluate(plan, task) for policy in self.policies]
