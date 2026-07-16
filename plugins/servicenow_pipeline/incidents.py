"""Incident service orchestration for the ServiceNow pipeline.

This module owns the incident workflow coordination layer. It stitches
together request validation, payload preparation, table execution, and result
processing while remaining independent of Hermes runtime and HTTP details.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import logging
from typing import Optional

from plugins.servicenow_pipeline.models import ExecutionResult, IncidentRequest
from plugins.servicenow_pipeline.payload_builder import PayloadBuilder
from plugins.servicenow_pipeline.table_executor import (
    TableExecutionConnectionError,
    TableExecutionRequestError,
    TableExecutor,
    TableRecord,
)
from plugins.servicenow_pipeline.tracing import elapsed_ms, log_stage, new_correlation_id, now, sanitize_payload

logger = logging.getLogger(__name__)


class IncidentServiceError(RuntimeError):
    """Base exception for incident service failures."""


class IncidentValidationError(IncidentServiceError):
    """Raised when the incident request does not meet minimal structural requirements."""


class IncidentExecutionError(IncidentServiceError):
    """Raised when orchestration or table execution fails."""


@dataclass(slots=True)
class IncidentService:
    """Orchestrates the incident workflow without owning transport or mapping.

    Dependencies are injected to keep the service reusable and independently
    testable.
    """

    payload_builder: PayloadBuilder
    table_executor: TableExecutor

    def create_incident(self, request: IncidentRequest, *, correlation_id: str | None = None) -> ExecutionResult:
        """Run the incident workflow and return a terminal execution result."""
        corr_id = correlation_id or new_correlation_id()
        start = now()
        log_stage(
            logger,
            stage="incident_service",
            correlation_id=corr_id,
            success=True,
            duration_ms=0.0,
            message="Incident workflow started",
            extra={"request": sanitize_payload(request)},
        )
        try:
            self.validate_request(request, correlation_id=corr_id)
            payload = self.prepare_payload(request, correlation_id=corr_id)

            # TODO: insert a future ReferenceResolver here for lookup-backed fields.
            record = self.execute_creation(payload, correlation_id=corr_id)
            result = self.process_result(record, correlation_id=corr_id)
            log_stage(
                logger,
                stage="incident_service",
                correlation_id=corr_id,
                success=True,
                duration_ms=elapsed_ms(start),
                message="Incident workflow completed",
                extra={"success": result.success, "incident_number": result.incident_number, "sys_id": result.sys_id},
            )
            return result
        except Exception as exc:
            log_stage(
                logger,
                stage="incident_service",
                correlation_id=corr_id,
                success=False,
                duration_ms=elapsed_ms(start),
                error=exc,
            )
            raise

    def validate_request(self, request: IncidentRequest, *, correlation_id: str | None = None) -> None:
        """Perform minimal structural validation for an incident request."""
        if not isinstance(request, IncidentRequest):
            raise IncidentValidationError("request must be an IncidentRequest.")
        if not str(request.short_description or "").strip():
            raise IncidentValidationError("short_description is required.")
        if not str(request.description or "").strip():
            raise IncidentValidationError("description is required.")
        if correlation_id:
            logger.debug(
                "ServiceNow trace: %s",
                {"stage": "incident_validation", "correlation_id": correlation_id, "success": True},
            )

    def prepare_payload(self, request: IncidentRequest, *, correlation_id: str | None = None):
        """Transform a validated request into a normalized payload."""
        try:
            start = now()
            payload = self.payload_builder.build_incident_payload(request, correlation_id=correlation_id)
            log_stage(
                logger,
                stage="payload_builder",
                correlation_id=correlation_id or new_correlation_id(),
                success=True,
                duration_ms=elapsed_ms(start),
                extra={"payload": sanitize_payload(payload)},
            )
            return payload
        except Exception as exc:
            raise IncidentExecutionError(f"Failed to prepare incident payload: {exc}") from exc

    def execute_creation(self, payload, *, correlation_id: str | None = None) -> TableRecord:
        """Execute the record creation step through the table executor."""
        try:
            start = now()
            record = self.table_executor.create_record(payload.table, asdict(payload), correlation_id=correlation_id)
            log_stage(
                logger,
                stage="table_executor",
                correlation_id=correlation_id or new_correlation_id(),
                success=True,
                duration_ms=elapsed_ms(start),
                extra={"table": payload.table, "record_id": record.record_id},
            )
            return record
        except (TableExecutionConnectionError, TableExecutionRequestError) as exc:
            raise IncidentExecutionError(f"Incident creation failed: {exc}") from exc
        except Exception as exc:
            raise IncidentExecutionError(f"Unexpected incident creation failure: {exc}") from exc

    def process_result(self, record: TableRecord, *, correlation_id: str | None = None) -> ExecutionResult:
        """Convert executor output into the incident service terminal result."""
        if not isinstance(record, TableRecord):
            raise IncidentExecutionError("table executor returned an invalid record.")

        incident_number = self._extract_incident_number(record)
        sys_id = record.record_id or self._extract_sys_id(record)
        message = "Incident creation completed."
        result = ExecutionResult(
            success=True,
            message=message,
            incident_number=incident_number,
            sys_id=sys_id,
        )
        if correlation_id:
            log_stage(
                logger,
                stage="incident_service",
                correlation_id=correlation_id,
                success=True,
                duration_ms=0.0,
                message="Incident result processed",
                extra={"incident_number": incident_number, "sys_id": sys_id},
            )
        return result

    def _extract_incident_number(self, record: TableRecord) -> Optional[str]:
        value = record.data.get("number")
        if value:
            return str(value)
        return None

    def _extract_sys_id(self, record: TableRecord) -> Optional[str]:
        value = record.data.get("sys_id") or record.data.get("sysId") or record.data.get("id")
        if value:
            return str(value)
        return None
