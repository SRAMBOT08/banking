import pytest
from httpx import ASGITransport, AsyncClient

from app.config.settings import Settings
from app.main import create_app
from app.repositories.inmemory import ExecutionRepository
from app.services.platform import ExecutionPlatformService


class _NoopPublisher:
    def __getattr__(self, _name):
        def _noop(*_args, **_kwargs):
            return None
        return _noop


@pytest.mark.asyncio
async def test_rest_endpoints_smoke():
    settings = Settings(kafka_bootstrap="")
    app = create_app(settings)
    repository = ExecutionRepository()
    platform = ExecutionPlatformService(settings, repository)
    app.state.settings = settings
    app.state.repository = repository
    app.state.platform = platform
    app.state.publisher = _NoopPublisher()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        assert (await client.get("/health")).status_code == 200
        assert (await client.get("/ready")).status_code == 200

        payload = {
            "payload": {
                "metadata": {"correlation_id": "corr-api", "tenant_id": "tenant-api"},
                "snapshot": {
                    "metadata": {"snapshot_id": "snap-api", "snapshot_version": 1, "investigation_id": "inv-api"},
                    "investigation": {"investigation_id": "inv-api"},
                    "confidence": {"score": 70},
                    "recommendations": [{"recommendation_id": "rec-api", "title": "SOC review", "scope": "soc"}],
                },
                "risk_score": 30,
            }
        }
        response = await client.post("/execution/plans", json=payload)
        assert response.status_code == 200

        assert (await client.get("/execution/plans")).status_code == 200
        assert (await client.get("/execution/tasks")).status_code == 200
        assert (await client.get("/execution/status")).status_code == 200
        assert (await client.get("/execution/metrics")).status_code == 200
        assert (await client.get("/execution/audit")).status_code == 200
        assert (await client.get("/execution/history")).status_code == 200
