"""Generic ServiceNow table executor.

This module provides a reusable CRUD boundary for arbitrary ServiceNow tables.
It intentionally contains no business rules, no payload mapping, and no
knowledge of any specific ServiceNow domain object.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import logging
from typing import Any, Mapping, Optional

from plugins.servicenow_pipeline.servicenow_client import (
    ConnectionError as ServiceNowConnectionError,
    RequestError as ServiceNowRequestError,
    ServiceNowClient,
    ServiceNowError,
)
from plugins.servicenow_pipeline.tracing import elapsed_ms, log_stage, new_correlation_id, now, sanitize_payload, sanitize_response

logger = logging.getLogger(__name__)


class TableExecutorError(RuntimeError):
    """Base exception for table execution failures."""


class TableExecutionRequestError(TableExecutorError):
    """Raised when a table operation cannot be prepared or completed."""


class TableExecutionConnectionError(TableExecutorError):
    """Raised when the underlying ServiceNow client cannot reach the instance."""


@dataclass(frozen=True, slots=True)
class TableRecord:
    """Generic table record wrapper returned by the executor.

    The executor stays agnostic to table semantics by preserving the raw record
    payload in a structured container.
    """

    table: str
    record_id: str | None = None
    data: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class TableQueryResult:
    """Generic query response wrapper for table searches."""

    table: str
    count: int
    records: tuple[TableRecord, ...] = ()


@dataclass(frozen=True, slots=True)
class TableDeleteResult:
    """Generic delete response wrapper."""

    table: str
    record_id: str
    deleted: bool
    message: str = ""


class TableExecutor:
    """Reusable CRUD executor for ServiceNow tables.

    The executor is intentionally generic: it delegates all transport details
    to :class:`ServiceNowClient` and only shapes table-oriented operations.
    """

    def __init__(self, client: ServiceNowClient, *, logger_: logging.Logger | None = None) -> None:
        self._client = client
        self._logger = logger_ or logger

    def create_record(
        self,
        table: str,
        payload: Mapping[str, Any],
        *,
        correlation_id: str | None = None,
    ) -> TableRecord:
        """Create a record in the requested table."""
        table_name = self._normalize_table(table)
        body = dict(payload)
        corr_id = correlation_id or new_correlation_id()
        start = now()
        log_stage(
            logger,
            stage="table_executor",
            correlation_id=corr_id,
            success=True,
            duration_ms=0.0,
            message="Table create started",
            extra={"table": table_name, "payload": sanitize_payload(body)},
        )
        try:
            response = self._client.request("POST", f"/api/now/table/{table_name}", json=body, correlation_id=corr_id)
        except ServiceNowConnectionError as exc:
            log_stage(
                logger,
                stage="table_executor",
                correlation_id=corr_id,
                success=False,
                duration_ms=elapsed_ms(start),
                error=exc,
                extra={"table": table_name},
            )
            raise TableExecutionConnectionError(str(exc)) from exc
        except ServiceNowRequestError as exc:
            log_stage(
                logger,
                stage="table_executor",
                correlation_id=corr_id,
                success=False,
                duration_ms=elapsed_ms(start),
                error=exc,
                extra={"table": table_name},
            )
            raise TableExecutionRequestError(str(exc)) from exc
        self._log_operation("create", table_name, response, correlation_id=corr_id, duration_ms=elapsed_ms(start))
        return self._record_from_response(table_name, response)

    def get_record(self, table: str, record_id: str, *, correlation_id: str | None = None) -> Optional[TableRecord]:
        """Fetch a single record by identifier."""
        table_name = self._normalize_table(table)
        sys_id = self._normalize_record_id(record_id)
        corr_id = correlation_id or new_correlation_id()
        start = now()
        try:
            response = self._client.request("GET", f"/api/now/table/{table_name}/{sys_id}", correlation_id=corr_id)
        except ServiceNowConnectionError as exc:
            raise TableExecutionConnectionError(str(exc)) from exc
        except ServiceNowRequestError as exc:
            raise TableExecutionRequestError(str(exc)) from exc
        self._log_operation("get", table_name, response, correlation_id=corr_id, duration_ms=elapsed_ms(start))
        if not response:
            return None
        return self._record_from_response(table_name, response)

    def update_record(
        self,
        table: str,
        record_id: str,
        payload: Mapping[str, Any],
        *,
        correlation_id: str | None = None,
    ) -> TableRecord:
        """Update a record in the requested table."""
        table_name = self._normalize_table(table)
        sys_id = self._normalize_record_id(record_id)
        corr_id = correlation_id or new_correlation_id()
        start = now()
        body = dict(payload)
        try:
            response = self._client.request("PATCH", f"/api/now/table/{table_name}/{sys_id}", json=body, correlation_id=corr_id)
        except ServiceNowConnectionError as exc:
            raise TableExecutionConnectionError(str(exc)) from exc
        except ServiceNowRequestError as exc:
            raise TableExecutionRequestError(str(exc)) from exc
        self._log_operation("update", table_name, response, correlation_id=corr_id, duration_ms=elapsed_ms(start))
        return self._record_from_response(table_name, response, fallback_record_id=sys_id)

    def delete_record(self, table: str, record_id: str, *, correlation_id: str | None = None) -> TableDeleteResult:
        """Delete a record from the requested table."""
        table_name = self._normalize_table(table)
        corr_id = correlation_id or new_correlation_id()
        start = now()
        sys_id = self._normalize_record_id(record_id)
        try:
            response = self._client.request("DELETE", f"/api/now/table/{table_name}/{sys_id}", correlation_id=corr_id)
        except ServiceNowConnectionError as exc:
            raise TableExecutionConnectionError(str(exc)) from exc
        except ServiceNowRequestError as exc:
            raise TableExecutionRequestError(str(exc)) from exc
        self._log_operation("delete", table_name, response, correlation_id=corr_id, duration_ms=elapsed_ms(start))
        deleted = bool(response.get("result") is None or response == {})
        message = str(response.get("message") or response.get("status") or "deleted")
        return TableDeleteResult(table=table_name, record_id=sys_id, deleted=deleted, message=message)

    def query_records(self, table: str, query: str, *, correlation_id: str | None = None) -> TableQueryResult:
        """Query records from the requested table."""
        table_name = self._normalize_table(table)
        corr_id = correlation_id or new_correlation_id()
        start = now()
        params = {"sysparm_query": str(query or "").strip()}
        try:
            response = self._client.request("GET", f"/api/now/table/{table_name}", params=params, correlation_id=corr_id)
        except ServiceNowConnectionError as exc:
            raise TableExecutionConnectionError(str(exc)) from exc
        except ServiceNowRequestError as exc:
            raise TableExecutionRequestError(str(exc)) from exc
        self._log_operation("query", table_name, response, correlation_id=corr_id, duration_ms=elapsed_ms(start))
        records = self._records_from_response(table_name, response)
        return TableQueryResult(table=table_name, count=len(records), records=records)

    def _normalize_table(self, table: str) -> str:
        normalized = str(table or "").strip()
        if not normalized:
            raise TableExecutionRequestError("table is required.")
        return normalized

    def _normalize_record_id(self, record_id: str) -> str:
        normalized = str(record_id or "").strip()
        if not normalized:
            raise TableExecutionRequestError("record_id is required.")
        return normalized

    def _record_from_response(
        self,
        table: str,
        response: Mapping[str, Any],
        *,
        fallback_record_id: str | None = None,
    ) -> TableRecord:
        payload = self._extract_result_payload(response)
        record_id = self._extract_record_id(payload) or fallback_record_id
        if isinstance(payload, Mapping):
            data = dict(payload)
        else:
            data = {"result": payload}
        return TableRecord(table=table, record_id=record_id, data=data)

    def _records_from_response(self, table: str, response: Mapping[str, Any]) -> tuple[TableRecord, ...]:
        payload = self._extract_result_payload(response)
        if isinstance(payload, list):
            return tuple(
                TableRecord(
                    table=table,
                    record_id=self._extract_record_id(item),
                    data=dict(item) if isinstance(item, Mapping) else {"result": item},
                )
                for item in payload
            )
        if isinstance(payload, Mapping):
            result = payload.get("result")
            if isinstance(result, list):
                return tuple(
                    TableRecord(
                        table=table,
                        record_id=self._extract_record_id(item),
                        data=dict(item) if isinstance(item, Mapping) else {"result": item},
                    )
                    for item in result
                )
            if isinstance(result, Mapping):
                return (self._record_from_response(table, payload),)
        if payload:
            return (TableRecord(table=table, record_id=self._extract_record_id(payload), data={"result": payload}),)
        return ()

    def _extract_result_payload(self, response: Mapping[str, Any]) -> Any:
        if isinstance(response, Mapping) and "result" in response:
            return response.get("result")
        return response

    def _extract_record_id(self, payload: Any) -> str | None:
        if isinstance(payload, Mapping):
            for key in ("sys_id", "sysId", "id"):
                value = payload.get(key)
                if value:
                    return str(value)
        return None

    def _log_operation(
        self,
        operation: str,
        table: str,
        response: Mapping[str, Any],
        *,
        correlation_id: str,
        duration_ms: float,
    ) -> None:
        log_stage(
            self._logger,
            stage="table_executor",
            correlation_id=correlation_id,
            success=True,
            duration_ms=duration_ms,
            message=f"Table {operation} completed",
            extra={
                "table": table,
                "response_keys": sorted(response.keys()) if isinstance(response, Mapping) else [],
                "response": sanitize_response(response),
            },
        )
