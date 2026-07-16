"""ServiceNow pipeline orchestration layer.

This module coordinates the ServiceNow capability flow without owning HTTP,
payload transformation, CRUD implementation, or verification logic.
"""

from __future__ import annotations

from dataclasses import dataclass
import logging
from typing import Any

from plugins.servicenow_pipeline.incidents import (
    IncidentExecutionError,
    IncidentService,
    IncidentServiceError,
)
from plugins.servicenow_pipeline.models import ExecutionResult, IncidentRequest, VerificationResult
from plugins.servicenow_pipeline.verifier import (
    ExecutionVerifier,
    VerificationError,
    VerificationRuleError,
)
from plugins.servicenow_pipeline.tracing import elapsed_ms, log_stage, new_correlation_id, now

logger = logging.getLogger(__name__)


class ServiceNowPipelineError(RuntimeError):
    """Base exception for pipeline orchestration failures."""


class ServiceNowPipelineExecutionError(ServiceNowPipelineError):
    """Raised when a pipeline execution step fails."""


@dataclass(slots=True)
class ServiceNowPipeline:
    """Thin orchestration layer for ServiceNow incident workflows.

    The pipeline coordinates the execution flow and delegates business logic
    and verification to injected collaborators.
    """

    incident_service: IncidentService
    verifier: ExecutionVerifier

    def execute(self, request: IncidentRequest, *, correlation_id: str | None = None) -> VerificationResult:
        """Run the ServiceNow pipeline and return the verification outcome."""
        corr_id = correlation_id or new_correlation_id()
        start = now()
        log_stage(
            logger,
            stage="pipeline_execution",
            correlation_id=corr_id,
            success=True,
            duration_ms=0.0,
            message="Pipeline execution started",
            extra={"component": "servicenow_pipeline"},
        )
        try:
            execution_result = self.execute_create_incident(request, correlation_id=corr_id)
            verification_result = self.verifier.verify_creation(execution_result, correlation_id=corr_id)
            log_stage(
                logger,
                stage="pipeline_completion",
                correlation_id=corr_id,
                success=True,
                duration_ms=elapsed_ms(start),
                message="Pipeline execution completed",
                extra={"verified": verification_result.verified},
            )
            return verification_result
        except (IncidentServiceError, VerificationError) as exc:
            return self.handle_failure(exc, correlation_id=corr_id, start=start)
        except Exception as exc:  # pragma: no cover - defensive guard
            return self.handle_failure(exc, correlation_id=corr_id, start=start)

    def execute_create_incident(
        self,
        request: IncidentRequest,
        *,
        correlation_id: str | None = None,
    ) -> ExecutionResult:
        """Execute the incident creation workflow through the incident service."""
        corr_id = correlation_id or new_correlation_id()
        start = now()
        log_stage(
            logger,
            stage="pipeline_execution",
            correlation_id=corr_id,
            success=True,
            duration_ms=0.0,
            message="Incident pipeline handoff started",
            extra={"component": "servicenow_pipeline"},
        )
        try:
            result = self.incident_service.create_incident(request, correlation_id=corr_id)
            log_stage(
                logger,
                stage="pipeline_execution",
                correlation_id=corr_id,
                success=True,
                duration_ms=elapsed_ms(start),
                message="Incident pipeline handoff completed",
                extra={"has_sys_id": bool(result.sys_id), "has_incident_number": bool(result.incident_number)},
            )
            return result
        except IncidentServiceError as exc:
            log_stage(
                logger,
                stage="pipeline_execution",
                correlation_id=corr_id,
                success=False,
                duration_ms=elapsed_ms(start),
                error=exc,
                extra={"component": "servicenow_pipeline"},
            )
            raise
        except Exception as exc:
            log_stage(
                logger,
                stage="pipeline_execution",
                correlation_id=corr_id,
                success=False,
                duration_ms=elapsed_ms(start),
                error=exc,
                extra={"component": "servicenow_pipeline"},
            )
            raise ServiceNowPipelineExecutionError(f"Pipeline execution failed: {exc}") from exc

    def handle_failure(
        self,
        exc: Exception,
        *,
        correlation_id: str | None = None,
        start: float | None = None,
    ) -> VerificationResult:
        """Convert lower-level failures into a terminal verification result."""
        message = str(exc).strip() or "ServiceNow pipeline execution failed."
        log_stage(
            logger,
            stage="pipeline_completion",
            correlation_id=correlation_id or new_correlation_id(),
            success=False,
            duration_ms=elapsed_ms(start) if start is not None else 0.0,
            error=exc,
            message=message,
            extra={"component": "servicenow_pipeline"},
        )
        return VerificationResult(verified=False, message=message)
