import pytest
from httpx import ASGITransport, AsyncClient

from app.config.settings import AdapterSettings
from app.main import create_app


@pytest.mark.asyncio
async def test_dry_run_endpoint_validates_and_returns_preview():
    settings = AdapterSettings(
        SERVICENOW_BASE_URL="https://example.service-now.com",
        SERVICENOW_USERNAME="user",
        SERVICENOW_PASSWORD="pass",
        KAFKA_BOOTSTRAP_SERVERS="",
    )
    app = create_app(settings)
    transport = ASGITransport(app=app)
    payload = {
        "task": {
            "execution_id": "exec",
            "task_id": "task",
            "investigation_id": "inv",
            "correlation_id": "corr",
            "tenant_id": "tenant",
            "operation": "CREATE_INCIDENT",
            "payload": {"short_description": "Incident from test", "snapshot_version": "1"},
            "priority": 80,
            "metadata": {},
        }
    }
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        result = await client.post("/dry-run", json=payload)
        assert result.status_code == 200
        body = result.json()
        assert body["preview"]["request"]["endpoint"] == "/api/now/table/incident"
