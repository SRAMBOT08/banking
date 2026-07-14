from __future__ import annotations

import time
from typing import Any

import httpx

from app.config import AdapterSettings
from app.logging.json_logger import get_logger
from app.models import ServiceNowRequest, ServiceNowResponse
from app.models.errors import AdapterError, AdapterErrorCode
from app.retry.engine import RetryEngine, RetryState


class ServiceNowRestClient:
    def __init__(self, settings: AdapterSettings, auth: tuple[str, str], retry_engine: RetryEngine):
        self.settings = settings
        self.retry_engine = retry_engine
        self.logger = get_logger("servicenow_client", settings.log_level)
        self._client = httpx.AsyncClient(
            base_url=settings.servicenow_base_url.rstrip("/"),
            timeout=settings.request_timeout_seconds,
            verify=settings.servicenow_verify_ssl,
            auth=auth,
            limits=httpx.Limits(max_connections=20, max_keepalive_connections=10),
        )

    async def close(self) -> None:
        await self._client.aclose()

    async def send(self, request: ServiceNowRequest, correlation_id: str, execution_id: str, task_id: str) -> ServiceNowResponse:
        state = RetryState()
        last_error: AdapterError | None = None
        while True:
            started = time.perf_counter()
            try:
                response = await self._client.request(
                    request.method,
                    request.endpoint,
                    params=request.query,
                    json=request.payload or None,
                    headers={
                        "Accept": "application/json",
                        "Content-Type": "application/json",
                        "X-Idempotency-Key": request.idempotency_key,
                        "X-Correlation-ID": correlation_id,
                        "X-Execution-ID": execution_id,
                        "X-Task-ID": task_id,
                    },
                )
                latency_ms = round((time.perf_counter() - started) * 1000, 3)
                if response.status_code in (401, 403):
                    code = AdapterErrorCode.AUTHENTICATION_FAILURE if response.status_code == 401 else AdapterErrorCode.AUTHORIZATION_FAILURE
                    raise AdapterError(code, "service now authorization failed", {"status_code": response.status_code})
                if response.status_code == 429:
                    raise AdapterError(AdapterErrorCode.RATE_LIMITING, "rate limited", {"status_code": response.status_code})
                if response.status_code == 409:
                    raise AdapterError(AdapterErrorCode.DUPLICATE_REQUEST, "duplicate request", {"status_code": response.status_code})
                if response.status_code >= 500:
                    raise AdapterError(AdapterErrorCode.SERVER_ERROR, "servicenow server error", {"status_code": response.status_code})
                if response.status_code >= 400:
                    raise AdapterError(AdapterErrorCode.UNEXPECTED_RESPONSE, "unexpected client response", {"status_code": response.status_code, "body": response.text[:300]})
                body = response.json() if response.content else {}
                if not isinstance(body, dict):
                    raise AdapterError(AdapterErrorCode.UNEXPECTED_RESPONSE, "response body must be an object")
                return ServiceNowResponse(
                    status_code=response.status_code,
                    latency_ms=latency_ms,
                    body=body,
                    headers={key: value for key, value in response.headers.items()},
                )
            except httpx.TimeoutException as exc:
                last_error = AdapterError(AdapterErrorCode.TIMEOUT, "request timed out", {"error": str(exc)})
            except httpx.NetworkError as exc:
                last_error = AdapterError(AdapterErrorCode.NETWORK_FAILURE, "network failure", {"error": str(exc)})
            except AdapterError as exc:
                last_error = exc

            assert last_error is not None
            retryable_status = int(last_error.details.get("status_code")) if "status_code" in last_error.details else None
            if not self.retry_engine.should_retry(retryable_status, last_error, state):
                if state.attempt > 0 and last_error.code in {AdapterErrorCode.TIMEOUT, AdapterErrorCode.NETWORK_FAILURE, AdapterErrorCode.SERVER_ERROR, AdapterErrorCode.RATE_LIMITING}:
                    raise AdapterError(AdapterErrorCode.RETRY_EXHAUSTION, "retry attempts exhausted", {"attempts": state.attempt + 1, "last_error": last_error.code.value})
                raise last_error
            state.attempt += 1
            await self.retry_engine.backoff(state)
