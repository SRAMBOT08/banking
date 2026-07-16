from __future__ import annotations

from typing import Any, Dict, List

from app.audit.store import ImmutableAuditStore
from app.logging.json_logger import get_logger
from app.mapper.servicenow_mapper import ServiceNowTaskMapper
from app.models import AuditRecord, ExecutionResult, ExecutionTask, OperationType
from app.models.errors import AdapterError, AdapterErrorCode
from app.operations.change.service import ChangeOperationService
from app.operations.cmdb.service import CmdbOperationService
from app.operations.incident.service import IncidentOperationService
from app.operations.user.service import UserOperationService
from app.verification.incident_verifier import IncidentVerifier


class ServiceNowAdapterService:
    def __init__(
        self,
        incident_ops: IncidentOperationService,
        user_ops: UserOperationService,
        cmdb_ops: CmdbOperationService,
        change_ops: ChangeOperationService,
        verifier: IncidentVerifier,
        mapper: ServiceNowTaskMapper,
        audit_store: ImmutableAuditStore,
        publisher,
        logger_level: str,
    ):
        self.incident_ops = incident_ops
        self.user_ops = user_ops
        self.cmdb_ops = cmdb_ops
        self.change_ops = change_ops
        self.verifier = verifier
        self.mapper = mapper
        self.audit_store = audit_store
        self.publisher = publisher
        self.logger = get_logger("servicenow_adapter_service", logger_level)

    def dry_run(self, task: ExecutionTask) -> Dict[str, Any]:
        return self.mapper.dry_run_preview(task)

    async def process_task(self, task: ExecutionTask) -> ExecutionResult:
        self.publisher.publish_started(
            {
                "execution_id": task.execution_id,
                "task_id": task.task_id,
                "investigation_id": task.investigation_id,
                "correlation_id": task.correlation_id,
                "tenant_id": task.tenant_id,
                "operation": task.operation.value,
            },
            task.execution_id,
        )
        request = self.mapper.map_to_request(task)
        try:
            if task.operation == OperationType.CREATE_INCIDENT:
                incident, latency_ms, method, endpoint, retry_count = await self.incident_ops.create(task)
                verification = await self.verifier.verify_created_incident(task, incident.sys_id)
                result = ExecutionResult(
                    execution_id=task.execution_id,
                    task_id=task.task_id,
                    operation=task.operation,
                    success=verification.verified,
                    sys_id=incident.sys_id,
                    result=incident.model_dump(mode="json"),
                    verification=verification,
                )
                self.publisher.publish_verified(
                    {
                        "execution_id": task.execution_id,
                        "task_id": task.task_id,
                        "verification": verification.model_dump(mode="json"),
                    },
                    task.execution_id,
                )
            elif task.operation == OperationType.GET_INCIDENT:
                body, latency_ms, method, endpoint, retry_count = await self.incident_ops.get(task)
                result = ExecutionResult(
                    execution_id=task.execution_id,
                    task_id=task.task_id,
                    operation=task.operation,
                    success=True,
                    sys_id=str(body.get("sys_id", "")) or None,
                    result=body,
                )
            elif task.operation == OperationType.UPDATE_INCIDENT:
                body, latency_ms, method, endpoint, retry_count = await self.incident_ops.update(task)
                result = ExecutionResult(
                    execution_id=task.execution_id,
                    task_id=task.task_id,
                    operation=task.operation,
                    success=True,
                    sys_id=str(body.get("sys_id", "")) or None,
                    result=body,
                )
            elif task.operation == OperationType.LOOKUP_USER:
                body, latency_ms, method, endpoint, retry_count = await self.user_ops.lookup(task)
                result = ExecutionResult(
                    execution_id=task.execution_id,
                    task_id=task.task_id,
                    operation=task.operation,
                    success=True,
                    result={"matches": body},
                )
            elif task.operation == OperationType.LOOKUP_CMDB_CI:
                body, latency_ms, method, endpoint, retry_count = await self.cmdb_ops.lookup(task)
                result = ExecutionResult(
                    execution_id=task.execution_id,
                    task_id=task.task_id,
                    operation=task.operation,
                    success=True,
                    result={"matches": body},
                )
            elif task.operation == OperationType.CREATE_CHANGE_REQUEST:
                body, latency_ms, method, endpoint, retry_count = await self.change_ops.create(task)
                result = ExecutionResult(
                    execution_id=task.execution_id,
                    task_id=task.task_id,
                    operation=task.operation,
                    success=True,
                    sys_id=str(body.get("sys_id", "")) or None,
                    result=body,
                )
            else:
                raise AdapterError(AdapterErrorCode.VALIDATION_FAILURE, "unsupported operation")

            self._append_audit(task, method, endpoint, latency_ms, retry_count, result.success, result.sys_id, None, result.verification.verified if result.verification else None)
            self.publisher.publish_completed(result.model_dump(mode="json"), task.execution_id)
            return result
        except AdapterError as exc:
            self._append_audit(task, request.method, request.endpoint, 0.0, 0, False, None, exc.code.value, None)
            failed = ExecutionResult(
                execution_id=task.execution_id,
                task_id=task.task_id,
                operation=task.operation,
                success=False,
                error_code=exc.code.value,
                error_message=exc.message,
            )
            self.publisher.publish_failed(failed.model_dump(mode="json"), task.execution_id)
            return failed

    def _append_audit(
        self,
        task: ExecutionTask,
        method: str,
        endpoint: str,
        latency_ms: float,
        retry_count: int,
        success: bool,
        sys_id: str | None,
        failure_reason: str | None,
        verification_result: bool | None,
    ) -> None:
        record = AuditRecord(
            execution_id=task.execution_id,
            task_id=task.task_id,
            investigation_id=task.investigation_id,
            correlation_id=task.correlation_id,
            servicenow_sys_id=sys_id,
            http_method=method,
            endpoint=endpoint,
            latency_ms=latency_ms,
            retry_count=retry_count,
            verification_result=verification_result,
            success=success,
            failure_reason=failure_reason,
        )
        self.audit_store.append(record)

    async def process_event(self, event: Dict[str, Any]) -> List[ExecutionResult]:
        tasks = self._extract_tasks(event)
        results: List[ExecutionResult] = []
        for task in tasks:
            results.append(await self.process_task(task))
        return results

    def _extract_tasks(self, event: Dict[str, Any]) -> List[ExecutionTask]:
        if isinstance(event.get("result"), dict):
            event = {**event, **event["result"]}
        if "operation" in event:
            return [ExecutionTask.model_validate(event)]
        if "task" in event:
            return [ExecutionTask.model_validate(event["task"])]
        if isinstance(event.get("tasks"), list):
            parsed: List[ExecutionTask] = []
            for item in event["tasks"]:
                payload = {
                    "execution_id": event.get("plan_id") or event.get("execution_id") or item.get("task_id"),
                    "task_id": item.get("task_id"),
                    "investigation_id": event.get("investigation_id"),
                    "correlation_id": event.get("correlation_id") or event.get("plan_id"),
                    "tenant_id": event.get("tenant_id", "tenant-unknown"),
                    "operation": item.get("metadata", {}).get("operation", "CREATE_INCIDENT"),
                    "payload": item.get("metadata", {}).get("payload", {}),
                    "priority": int(item.get("priority", 50)),
                    "metadata": item.get("metadata", {}),
                }
                parsed.append(ExecutionTask.model_validate(payload))
            return parsed
        raise AdapterError(AdapterErrorCode.VALIDATION_FAILURE, "execution event has no executable task")
