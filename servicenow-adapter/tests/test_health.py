import pytest
import httpx

from app.client.rest_client import ServiceNowRestClient
from app.config.settings import AdapterSettings
from app.health.service import HealthService
from app.models import RetryPolicy
from app.retry.engine import RetryEngine


@pytest.mark.asyncio
async def test_health_reports_ok_when_servicenow_reachable():
    settings = AdapterSettings(
        SERVICENOW_BASE_URL="https://example.service-now.com",
        SERVICENOW_USERNAME="user",
        SERVICENOW_PASSWORD="pass",
        KAFKA_BOOTSTRAP_SERVERS="",
    )
    client = ServiceNowRestClient(settings, ("user", "pass"), RetryEngine(RetryPolicy(max_retries=0)))

    async def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"result": []})

    client._client = httpx.AsyncClient(base_url=settings.servicenow_base_url.rstrip("/"), transport=httpx.MockTransport(handler))
    response = await HealthService(settings, client).check()
    assert response.status == "ok"
    assert response.auth_ok
    await client.close()
