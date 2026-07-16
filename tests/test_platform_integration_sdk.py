from __future__ import annotations

from threading import Event

import httpx
import pytest
from pydantic import BaseModel

from shared.integration import (
    BaseQueryClient,
    CircuitBreaker,
    CircuitOpenError,
    ClientFactory,
    EndpointDefinition,
    EndpointRegistry,
    IntegrationSettings,
    IntegrationTimeoutError,
    ResponseMapper,
    RetryPolicy,
    ServiceDefinition,
    ServiceRegistry,
    TimeoutConfig,
    HttpClient,
)
from shared.integration.mapping import RequestMapper
from shared.integration.resilience.circuit_breaker import CircuitState


class Item(BaseModel):
    value: int


def test_http_client_serializes_json_and_propagates_headers_and_correlation():
    seen = []

    def handler(request):
        seen.append(request)
        return httpx.Response(200, json={"items": [{"value": 3}]}, request=request)

    client = HttpClient("http://platform", client=httpx.Client(base_url="http://platform", transport=httpx.MockTransport(handler)), timeout=TimeoutConfig(read=2))
    payload = client.post("/query", json={"value": 3}, correlation_id="corr-1", version="v1")

    assert payload["items"][0]["value"] == 3
    assert seen[0].headers["X-Correlation-ID"] == "corr-1"
    assert seen[0].headers["X-API-Version"] == "v1"
    assert seen[0].read().decode() == '{"value":3}'


def test_http_client_retries_configured_exceptions():
    attempts = []

    def handler(request):
        attempts.append(request)
        if len(attempts) == 1:
            raise httpx.ConnectError("temporary", request=request)
        return httpx.Response(200, json={"ok": True}, request=request)

    policy = RetryPolicy(max_attempts=2, base_delay=0, retryable_exceptions=(httpx.ConnectError,))
    client = HttpClient("http://platform", client=httpx.Client(base_url="http://platform", transport=httpx.MockTransport(handler)), retry_policy=policy)
    assert client.get("/health")["ok"] is True
    assert len(attempts) == 2


def test_cancellation_stops_before_dispatch():
    event = Event()
    event.set()
    client = HttpClient("http://platform", client=httpx.Client(transport=httpx.MockTransport(lambda request: httpx.Response(200, json={}))))

    with pytest.raises(IntegrationTimeoutError):
        client.get("/query", cancel_event=event)


def test_circuit_breaker_transitions_closed_open_half_open():
    breaker = CircuitBreaker(failure_threshold=1, recovery_timeout=0)
    breaker.record_failure()
    assert breaker.state is CircuitState.OPEN
    assert breaker.allow_request() is True
    breaker.record_success()
    assert breaker.state is CircuitState.CLOSED
    breaker.record_failure()
    breaker.recovery_timeout = 999
    with pytest.raises(CircuitOpenError):
        breaker.before_call()


def test_response_and_request_mappers_are_typed():
    response = ResponseMapper(Item).map({"value": 9})
    request = RequestMapper(lambda value: {"wrapped": value}).map(4)
    assert response.value == 9
    assert request == {"wrapped": 4}


def test_query_client_supports_get_post_and_search():
    calls = []

    def handler(request):
        calls.append(request)
        return httpx.Response(200, json={"items": []}, request=request)

    query = BaseQueryClient("test", HttpClient("http://platform", client=httpx.Client(base_url="http://platform", transport=httpx.MockTransport(handler))))
    query.get("/metadata", params={"tenant_id": "t"})
    query.post("/search", request={"query": "x"})
    query.search("/search", {"query": "y"})
    assert [request.method for request in calls] == ["GET", "POST", "POST"]


def test_registries_and_factory_are_dependency_injected():
    services = ServiceRegistry({"evidence": ServiceDefinition("evidence", "http://evidence")})
    assert set(services.names()) >= {"evidence", "threat", "knowledge", "graph", "memory", "ai", "execution"}
    endpoints = EndpointRegistry([EndpointDefinition("evidence", "search", "POST", "/api/v1/evidence/search")])
    assert endpoints.get("evidence", "search").path == "/api/v1/evidence/search"
    settings = IntegrationSettings(service_urls={"evidence": "http://evidence"}, retry_max_attempts=1)
    client = ClientFactory(settings).create_query_client("evidence")
    assert isinstance(client, BaseQueryClient)
    client.close()
