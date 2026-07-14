from __future__ import annotations

from app.client.rest_client import ServiceNowRestClient
from app.models import ExecutionTask
from app.mapper.servicenow_mapper import ServiceNowTaskMapper


class ChangeOperationService:
    def __init__(self, client: ServiceNowRestClient, mapper: ServiceNowTaskMapper):
        self.client = client
        self.mapper = mapper

    async def create(self, task: ExecutionTask):
        request = self.mapper.map_to_request(task)
        response = await self.client.send(request, task.correlation_id, task.execution_id, task.task_id)
        return response.body.get("result", {}), response.latency_ms, request.method, request.endpoint, 0
