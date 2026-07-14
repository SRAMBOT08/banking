from __future__ import annotations

from datetime import datetime, timedelta, timezone

from app.config.settings import Settings
from app.models import (
    ApprovalDecision,
    ApprovalStatus,
    ExecutionCategory,
    ExecutionPlan,
    ExecutionTask,
    PolicyDecision,
    PolicyStatus,
)
from app.policies.base import ApprovalPolicy


class DeterministicApprovalPolicy(ApprovalPolicy):
    name = "deterministic_approval_policy"

    def __init__(self, settings: Settings):
        self.settings = settings

    def _required_approvers(self, task: ExecutionTask):
        if task.category == ExecutionCategory.FRAUD:
            return ["FRAUD_APPROVER"]
        if task.category == ExecutionCategory.COMPLIANCE:
            return ["COMPLIANCE_APPROVER", "MANAGER_APPROVER"]
        if task.category == ExecutionCategory.SOC:
            return ["SOC_APPROVER"]
        if task.category == ExecutionCategory.SECURITY:
            return ["SECURITY_APPROVER"]
        if task.category == ExecutionCategory.RISK:
            return ["RISK_APPROVER"]
        return ["MANAGER_APPROVER"]

    def evaluate(self, plan: ExecutionPlan, task: ExecutionTask) -> ApprovalDecision:
        auto = plan.risk_score <= self.settings.risk_auto_approve_threshold
        status = ApprovalStatus.AUTO_APPROVED if auto else ApprovalStatus.PENDING
        approvers = [] if auto else self._required_approvers(task)
        now = datetime.now(timezone.utc)
        return ApprovalDecision(
            correlation_id=plan.correlation_id,
            investigation_id=plan.investigation_id,
            tenant_id=plan.tenant_id,
            plan_id=plan.plan_id,
            task_id=task.task_id,
            status=status,
            required_approvers=approvers,
            approved_by=[] if not auto else ["SYSTEM_AUTO_APPROVAL"],
            approval_history=[{
                "action": "AUTO_APPROVED" if auto else "PENDING",
                "timestamp": now.isoformat(),
                "reason": "risk threshold" if auto else "manual approval required",
            }],
            expires_at=(now + timedelta(minutes=self.settings.approval_expiry_minutes)).isoformat(),
            explanation="Automatic approval granted" if auto else "Manual approval required by role policy",
        )


def requires_approval(policy_decisions: list[PolicyDecision]) -> bool:
    return any(decision.status == PolicyStatus.APPROVAL_REQUIRED for decision in policy_decisions)


def is_blocked(policy_decisions: list[PolicyDecision]) -> bool:
    return any(decision.status in {PolicyStatus.BLOCKED, PolicyStatus.DENIED, PolicyStatus.EXPIRED, PolicyStatus.UNSUPPORTED} for decision in policy_decisions)
