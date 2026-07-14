import pytest
import httpx

from app.client.rest_client import ServiceNowRestClient
from app.config.settings import AdapterSettings
from app.models import ExecutionTask, OperationType, RetryPolicy
from app.retry.engine import RetryEngine
from app.verification.incident_verifier import IncidentVerifier


@pytest.mark.asyncio
async def test_incident_verification_success():
    settings = AdapterSettings(
        SERVICENOW_BASE_URL="https://example.service-now.com",
        SERVICENOW_USERNAME="user",
        SERVICENOW_PASSWORD="pass",
        KAFKA_BOOTSTRAP_SERVERS="",
    )
    client = ServiceNowRestClient(settings, ("user", "pass"), RetryEngine(RetryPolicy(max_retries=0)))

    async def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"result": {"sys_id": "abc", "u_correlation_id": "corr", "u_investigation_id": "inv", "state": "2"}})

    client._client = httpx.AsyncClient(base_url=settings.servicenow_base_url.rstrip("/"), transport=httpx.MockTransport(handler))

    task = ExecutionTask(
        execution_id="exec",
        task_id="task",
        investigation_id="inv",
        correlation_id="corr",
        tenant_id="tenant",
        operation=OperationType.CREATE_INCIDENT,
        payload={},
        priority=1,
    )
    result = await IncidentVerifier(client).verify_created_incident(task, "abc")
    assert result.verified
    await client.close()
