from __future__ import annotations

from collections.abc import Mapping
from typing import Any
import httpx

from ..exceptions import IntegrationException, IntegrationTimeoutError, ServiceException
from ..resilience import CircuitBreaker, RetryPolicy, TimeoutConfig
from .authentication import Authentication
from .headers import build_headers
from .response_parser import ResponseParser


class HttpClient:
    """Business-logic-free HTTP transport used by every Platform client."""

    def __init__(self, base_url: str, *, timeout: TimeoutConfig | None = None, retry_policy: RetryPolicy | None = None, authentication: Authentication | None = None, headers: Mapping[str, str] | None = None, client: httpx.Client | None = None, circuit_breaker: CircuitBreaker | None = None):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout or TimeoutConfig()
        self.retry_policy = retry_policy or RetryPolicy(max_attempts=1)
        self.authentication = authentication
        self.headers = dict(headers or {})
        self.client = client or httpx.Client(base_url=self.base_url, timeout=httpx.Timeout(self.timeout.read, connect=self.timeout.connect, write=self.timeout.write, pool=self.timeout.pool))
        self.circuit_breaker = circuit_breaker
        self.parser = ResponseParser()

    def request(self, method: str, path: str, *, params: Mapping[str, Any] | None = None, json: Any = None, correlation_id: str | None = None, version: str | None = None, cancel_event: Any = None) -> Mapping[str, Any]:
        if cancel_event is not None and cancel_event.is_set():
            raise IntegrationTimeoutError("request cancelled before dispatch", endpoint=path)
        if self.circuit_breaker:
            self.circuit_breaker.before_call()
        url = path if path.startswith("http") else path
        request_headers = build_headers(self.headers, self.authentication.headers() if self.authentication else None, correlation_id=correlation_id, version=version)
        last_error: BaseException | None = None
        for attempt in range(1, self.retry_policy.max_attempts + 1):
            try:
                if cancel_event is not None and cancel_event.is_set():
                    raise IntegrationTimeoutError("request cancelled", endpoint=path)
                response = self.client.request(method.upper(), url, params=params, json=json, headers=request_headers, timeout=httpx.Timeout(self.timeout.read, connect=self.timeout.connect, write=self.timeout.write, pool=self.timeout.pool))
                payload = self.parser.parse(response, service=self.base_url, endpoint=path)
                if self.circuit_breaker:
                    self.circuit_breaker.record_success()
                return payload
            except (httpx.HTTPError, IntegrationException) as exc:
                last_error = exc
                if not self.retry_policy.should_retry(exc, attempt):
                    if self.circuit_breaker:
                        self.circuit_breaker.record_failure()
                    if isinstance(exc, IntegrationException):
                        raise
                    if isinstance(exc, httpx.TimeoutException):
                        raise IntegrationTimeoutError("request timed out", endpoint=path, cause=exc) from exc
                    raise ServiceException("HTTP request failed", endpoint=path, cause=exc) from exc
                import time
                time.sleep(self.retry_policy.delay(attempt))
        raise ServiceException("request failed after retries", endpoint=path, cause=last_error)

    def get(self, path: str, **kwargs) -> Mapping[str, Any]:
        return self.request("GET", path, **kwargs)

    def post(self, path: str, **kwargs) -> Mapping[str, Any]:
        return self.request("POST", path, **kwargs)

    def close(self) -> None:
        self.client.close()
