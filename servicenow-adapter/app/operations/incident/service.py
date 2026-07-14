from __future__ import annotations

from app.client.rest_client import ServiceNowRestClient
from app.models import ExecutionTask, IncidentResponse
from app.models.errors import AdapterError, AdapterErrorCode
from app.mapper.servicenow_mapper import ServiceNowTaskMapper


class IncidentOperationService:
    def __init__(self, client: ServiceNowRestClient, mapper: ServiceNowTaskMapper):
        self.client = client
        self.mapper = mapper

    async def create(self, task: ExecutionTask) -> tuple[IncidentResponse, float, str, str, int]:
        request = self.mapper.map_to_request(task)
        response = await self.client.send(request, task.correlation_id, task.execution_id, task.task_id)
        result = response.body.get("result")
        if not isinstance(result, dict) or not result.get("sys_id"):
            raise AdapterError(AdapterErrorCode.UNEXPECTED_RESPONSE, "create incident response missing sys_id")
        incident = IncidentResponse.model_validate(result)
        return incident, response.latency_ms, request.method, request.endpoint, 0

    async def get(self, task: ExecutionTask):
        request = self.mapper.map_to_request(task)
        response = await self.client.send(request, task.correlation_id, task.execution_id, task.task_id)
        return response.body.get("result", {}), response.latency_ms, request.method, request.endpoint, 0

    async def update(self, task: ExecutionTask):
        request = self.mapper.map_to_request(task)
        response = await self.client.send(request, task.correlation_id, task.execution_id, task.task_id)
        return response.body.get("result", {}), response.latency_ms, request.method, request.endpoint, 0
