from __future__ import annotations

from app.models import ExecutionResult, ExecutionVerification, VerificationStatus


class ExecutionVerificationEngine:
    def verify(self, result: ExecutionResult) -> ExecutionVerification:
        expected = result.expected_result or {}
        observed = result.observed_result or {}
        mismatches = [key for key, value in expected.items() if observed.get(key) != value]

        if not expected:
            status = VerificationStatus.INSUFFICIENT
        elif mismatches:
            status = VerificationStatus.MISMATCH
        else:
            status = VerificationStatus.VERIFIED

        return ExecutionVerification(
            correlation_id=result.correlation_id,
            investigation_id=result.investigation_id,
            tenant_id=result.tenant_id,
            plan_id=result.plan_id,
            task_id=result.task_id,
            verification_status=status,
            mismatch_details=[f"Mismatch for {item}" for item in mismatches],
        )
