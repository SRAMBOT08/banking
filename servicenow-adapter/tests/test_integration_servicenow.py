import os

import pytest

from app.client.rest_client import ServiceNowRestClient
from app.config.settings import AdapterSettings
from app.models import ExecutionTask, OperationType, RetryPolicy
from app.retry.engine import RetryEngine
from app.verification.incident_verifier import IncidentVerifier
from app.mapper.servicenow_mapper import ServiceNowTaskMapper


@pytest.mark.asyncio
async def test_live_servicenow_incident_roundtrip_when_configured():
    if os.getenv("SERVICENOW_LIVE_TEST", "false").lower() != "true":
        pytest.skip("SERVICENOW_LIVE_TEST not enabled")

    settings = AdapterSettings()
    client = ServiceNowRestClient(settings, (settings.servicenow_username, settings.servicenow_password), RetryEngine(RetryPolicy(max_retries=1)))
    task = ExecutionTask(
        execution_id="live-exec-1",
        task_id="live-task-1",
        investigation_id="live-inv-1",
        correlation_id="live-corr-1",
        tenant_id="tenant-live",
        operation=OperationType.CREATE_INCIDENT,
        payload={"short_description": "SentinelIQ live integration test", "snapshot_version": "1"},
        priority=80,
    )
    request = ServiceNowTaskMapper().map_to_request(task)
    response = await client.send(request, task.correlation_id, task.execution_id, task.task_id)
    sys_id = response.body.get("result", {}).get("sys_id")
    assert sys_id
    verification = await IncidentVerifier(client).verify_created_incident(task, sys_id)
    assert verification.verified
    await client.close()
