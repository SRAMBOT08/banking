from __future__ import annotations
from typing import Any
from ..base import BaseQueryClient
from ..observability import StructuredLogger
from ..resilience import RetryPolicy, TimeoutConfig
from ..transport import Authentication, HttpClient
from .integration_settings import IntegrationSettings


class ClientFactory:
    def __init__(self, settings: IntegrationSettings, *, authentication: Authentication | None = None, client_factory=None):
        self.settings = settings
        self.authentication = authentication
        self.client_factory = client_factory

    def create_query_client(self, service: str) -> BaseQueryClient:
        base_url = self.settings.service_urls[service]
        transport = (self.client_factory or HttpClient)(
            base_url,
            timeout=TimeoutConfig(connect=self.settings.timeout_seconds, read=self.settings.timeout_seconds, write=self.settings.timeout_seconds, pool=self.settings.timeout_seconds),
            retry_policy=RetryPolicy(max_attempts=self.settings.retry_max_attempts, base_delay=self.settings.retry_base_delay, max_delay=self.settings.retry_max_delay),
            authentication=self.authentication,
        )
        return BaseQueryClient(service, transport, logger=StructuredLogger(service))

    def create_tool_client(self, service: str, **kwargs):
        return self.create_query_client(service)
