"""Verification layer for the ServiceNow pipeline.

The verifier is responsible only for determining whether an execution
completed successfully. It does not call ServiceNow, modify records, or own
any request/response transport logic.
"""

from __future__ import annotations

from dataclasses import dataclass
import logging
from typing import Optional

from plugins.servicenow_pipeline.models import ExecutionResult, VerificationResult
from plugins.servicenow_pipeline.tracing import elapsed_ms, log_stage, new_correlation_id, now

logger = logging.getLogger(__name__)


class VerificationError(RuntimeError):
    """Base exception for verifier failures."""


class VerificationRuleError(VerificationError):
    """Raised when a required verification rule is not satisfied."""


@dataclass(slots=True)
class ExecutionVerifier:
    """Lightweight verification layer for ServiceNow executions.

    The MVP only checks the terminal execution state and the presence of the
    identifiers needed to consider the operation complete.
    """

    def verify_creation(
        self,
        result: ExecutionResult,
        *,
        correlation_id: str | None = None,
    ) -> VerificationResult:
        """Verify a creation result using the MVP rule set."""
        corr_id = correlation_id or new_correlation_id()
        start = now()
        try:
            self.verify_response(result)
            self.verify_required_fields(result)
            verification = self.build_verification_result(result)
            log_stage(
                logger,
                stage="verification",
                correlation_id=corr_id,
                success=True,
                duration_ms=elapsed_ms(start),
                message="Verification completed",
                extra={"verified": verification.verified},
            )
            return verification
        except Exception as exc:
            log_stage(
                logger,
                stage="verification",
                correlation_id=corr_id,
                success=False,
                duration_ms=elapsed_ms(start),
                error=exc,
            )
            raise

    def verify_response(self, result: ExecutionResult) -> None:
        """Validate the execution response shape and success state."""
        if not isinstance(result, ExecutionResult):
            raise VerificationRuleError("result must be an ExecutionResult.")
        if not result.success:
            message = str(result.message or "Execution was not successful.").strip()
            raise VerificationRuleError(message)
        if str(result.message or "").strip() == "":
            raise VerificationRuleError("ExecutionResult.message is required.")

    def verify_required_fields(self, result: ExecutionResult) -> None:
        """Verify the MVP-required identifiers are present.

        TODO: add reference validation, post-create GET verification, business
        rule verification, SLA verification, attachment verification, audit log
        verification, and retry verification.
        """
        if not str(result.sys_id or "").strip():
            raise VerificationRuleError("ExecutionResult.sys_id is required for verification.")
        if not str(result.incident_number or "").strip():
            raise VerificationRuleError(
                "ExecutionResult.incident_number is required for verification."
            )

    def build_verification_result(self, result: ExecutionResult) -> VerificationResult:
        """Build the terminal verification result for the pipeline."""
        if not isinstance(result, ExecutionResult):
            raise VerificationRuleError("result must be an ExecutionResult.")
        return VerificationResult(
            verified=True,
            message=str(result.message).strip() or "Execution verified successfully.",
        )
