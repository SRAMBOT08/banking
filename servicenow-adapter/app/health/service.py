from __future__ import annotations

from app.config import AdapterSettings
from app.models import HealthResponse, ServiceNowRequest
from app.client.rest_client import ServiceNowRestClient
from app.models.errors import AdapterError


class HealthService:
    def __init__(self, settings: AdapterSettings, client: ServiceNowRestClient):
        self.settings = settings
        self.client = client

    async def check(self) -> HealthResponse:
        configuration_valid = bool(self.settings.servicenow_base_url and self.settings.servicenow_username)
        auth_ok = False
        reachable = False
        if configuration_valid:
            request = ServiceNowRequest(
                method="GET",
                endpoint="/api/now/table/sys_user",
                query={"sysparm_limit": 1},
                idempotency_key="health-check",
            )
            try:
                response = await self.client.send(request, "health", "health", "health")
                auth_ok = response.status_code == 200
                reachable = response.status_code == 200
            except AdapterError:
                auth_ok = False
                reachable = False
        status = "ok" if configuration_valid and auth_ok and reachable else "degraded"
        return HealthResponse(
            status=status,
            service=self.settings.service_name,
            auth_ok=auth_ok,
            servicenow_reachable=reachable,
            configuration_valid=configuration_valid,
        )
