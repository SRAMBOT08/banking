from __future__ import annotations
from ..models import CaseFileInput, CasePolicyDecision, ExecutionAction, PolicyOutcome


class CasePolicyEngine:
    def __init__(self, auto_approve_severities=('low', 'medium'), approval_severities=('high',), denied_severities=('critical',)):
        self.auto_approve_severities = frozenset(auto_approve_severities); self.approval_severities = frozenset(approval_severities); self.denied_severities = frozenset(denied_severities)
    def evaluate(self, case_file: CaseFileInput, action: ExecutionAction) -> CasePolicyDecision:
        severity = str(case_file.metadata.get('severity', 'unknown')).lower()
        if severity in self.denied_severities:
            return CasePolicyDecision(policy_id='risk-threshold', outcome=PolicyOutcome.DENIED, reason='Case severity is blocked by risk policy.', rules=('critical-risk-block',))
        if severity in self.approval_severities:
            return CasePolicyDecision(policy_id='risk-threshold', outcome=PolicyOutcome.REQUIRES_APPROVAL, reason='Case severity requires human approval before execution.', rules=('high-risk-approval',), requires_approval=True)
        if severity in self.auto_approve_severities:
            return CasePolicyDecision(policy_id='risk-threshold', outcome=PolicyOutcome.ALLOWED, reason='Case severity is eligible for automatic approval.', rules=('standard-risk-allow',))
        return CasePolicyDecision(policy_id='risk-threshold', outcome=PolicyOutcome.DEFERRED, reason='Unknown severity is deferred until policy ownership confirms execution.', rules=('unknown-risk-defer',))
