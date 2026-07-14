from __future__ import annotations

from app.client.rest_client import ServiceNowRestClient
from app.models import ExecutionTask, VerificationResult
from app.models.errors import AdapterError, AdapterErrorCode


class IncidentVerifier:
    def __init__(self, client: ServiceNowRestClient):
        self.client = client

    async def verify_created_incident(self, task: ExecutionTask, sys_id: str) -> VerificationResult:
        endpoint = f"/api/now/table/incident/{sys_id}"
        from app.models import ServiceNowRequest

        request = ServiceNowRequest(method="GET", endpoint=endpoint, idempotency_key=task.execution_id)
        response = await self.client.send(request, task.correlation_id, task.execution_id, task.task_id)
        result = response.body.get("result")
        if not isinstance(result, dict):
            raise AdapterError(AdapterErrorCode.UNEXPECTED_RESPONSE, "verification response missing result object")

        sys_id_match = str(result.get("sys_id", "")) == sys_id
        correlation_match = str(result.get("u_correlation_id", "")) == task.correlation_id
        investigation_match = str(result.get("u_investigation_id", "")) == task.investigation_id
        state_value = str(result.get("state", ""))
        status_valid = state_value not in {"7", "8"}
        verified = sys_id_match and correlation_match and investigation_match and status_valid
        reason = "verified" if verified else "verification mismatch"
        return VerificationResult(
            verified=verified,
            reason=reason,
            sys_id=sys_id,
            correlation_id_match=correlation_match,
            investigation_id_match=investigation_match,
            execution_status_valid=status_valid,
        )
