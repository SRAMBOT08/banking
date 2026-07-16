from __future__ import annotations
from typing import Any
import httpx
from ..models import AdapterOperation, ExecutionAction
from .base import ExecutionAdapter, AdapterResult


class ServiceNowAdapter(ExecutionAdapter):
    OPERATIONS = frozenset(AdapterOperation)
    def __init__(self, base_url: str, username: str = '', password: str = '', timeout: float = 20): self.base_url, self.auth, self.timeout = base_url.rstrip('/'), (username, password), timeout
    def supports(self, operation: AdapterOperation) -> bool: return operation in self.OPERATIONS
    async def execute(self, execution_id: str, action: ExecutionAction) -> AdapterResult:
        if not self.supports(action.operation): raise ValueError(f'unsupported ServiceNow operation: {action.operation}')
        endpoint, method, payload = self._request(action)
        async with httpx.AsyncClient(timeout=self.timeout, auth=self.auth) as client:
            response = await client.request(method, f'{self.base_url}{endpoint}', json=payload)
            response.raise_for_status()
        return AdapterResult(execution_id=execution_id, action_id=str(action.action_id), operation=action.operation.value, response=response.json())
    def _request(self, action: ExecutionAction) -> tuple[str, str, dict[str, Any]]:
        payload = dict(action.payload)
        incident = payload.get('incident_id') or payload.get('sys_id')
        if action.operation == AdapterOperation.CREATE_INCIDENT: return '/api/now/table/incident', 'POST', payload
        if action.operation == AdapterOperation.RETRIEVE_STATUS: return f'/api/now/table/incident/{incident}', 'GET', {}
        if action.operation == AdapterOperation.UPDATE_INCIDENT: return f'/api/now/table/incident/{incident}', 'PATCH', payload
        if action.operation == AdapterOperation.ADD_WORK_NOTE: return f'/api/now/table/incident/{incident}', 'PATCH', {'work_notes': payload.get('work_notes', action.description)}
        if action.operation == AdapterOperation.ASSIGN_GROUP: return f'/api/now/table/incident/{incident}', 'PATCH', {'assignment_group': payload.get('assignment_group')}
        return f'/api/now/table/incident/{incident}', 'PATCH', {'state': '7'}
