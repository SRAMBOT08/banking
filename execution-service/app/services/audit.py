from __future__ import annotations

from typing import Any

from app.models import ExecutionAuditRecord


class ExecutionAuditEngine:
    def record(self, *, correlation_id: str, investigation_id: str, tenant_id: str, plan_id: str,
               reason: str, event_type: str, task_id: str | None = None, operator: str = "system",
               details: dict[str, Any] | None = None) -> ExecutionAuditRecord:
        return ExecutionAuditRecord(
            correlation_id=correlation_id,
            investigation_id=investigation_id,
            tenant_id=tenant_id,
            plan_id=plan_id,
            task_id=task_id,
            operator=operator,
            reason=reason,
            event_type=event_type,
            details=details or {},
        )
