from __future__ import annotations

from typing import Any, Dict, Mapping, Optional, Protocol

from shared.integration import (
    BaseQueryClient,
    CircuitBreaker,
    ClientFactory,
    EndpointDefinition,
    EndpointRegistry,
    IntegrationException,
    IntegrationSettings,
    HttpClient,
    RequestMapper,
    ResponseMapper,
    RetryPolicy,
    ServiceRegistry,
    ServiceDefinition,
    StructuredLogger,
    TimeoutConfig,
)

from .interfaces import GraphTool
from ..state import InvestigationState


class GraphToolError(RuntimeError):
    """Raised when Graph Intelligence cannot fulfill a query."""


class GraphServiceClient(Protocol):
    def get(self, path: str, *, params: Optional[Dict[str, Any]] = None, cancel_event: Any = None, correlation_id: str | None = None, **kwargs) -> Mapping[str, Any]: ...
    def post(self, path: str, request: Any = None, *, cancel_event: Any = None, correlation_id: str | None = None, **kwargs) -> Mapping[str, Any]: ...


class GraphServiceHTTPClient(BaseQueryClient):
    """Transport-only Graph Query API client built on the shared SDK."""

    def __init__(self, base_url: str, *, timeout_seconds: float = 10.0, retry_policy: RetryPolicy | None = None, circuit_breaker: CircuitBreaker | None = None, client: Any = None):
        transport = HttpClient(
            base_url,
            timeout=TimeoutConfig(connect=timeout_seconds, read=timeout_seconds, write=timeout_seconds, pool=timeout_seconds),
            retry_policy=retry_policy or RetryPolicy(max_attempts=3),
            circuit_breaker=circuit_breaker or CircuitBreaker(),
            client=client,
        )
        super().__init__(
            "graph",
            transport,
            request_mapper=RequestMapper(function=lambda value: value),
            response_mapper=ResponseMapper(function=lambda value: value),
            logger=StructuredLogger("graph"),
        )

    @classmethod
    def from_settings(cls, settings: IntegrationSettings, *, authentication=None) -> BaseQueryClient:
        return ClientFactory(settings, authentication=authentication).create_query_client("graph")


class GraphToolAdapter(GraphTool):
    """Thin translation boundary from Agent graph requests to Query API calls."""

    ENDPOINTS = {
        "node": ("GET", "/api/v1/graph/node/{node_id}"),
        "neighborhood": ("GET", "/api/v1/graph/node/{node_id}/neighbors"),
        "timeline": ("GET", "/api/v1/graph/node/{node_id}/timeline"),
        "path": ("GET", "/api/v1/graph/path"),
        "community": ("GET", "/api/v1/graph/community/{node_id}"),
        "component": ("GET", "/api/v1/graph/component/{node_id}"),
        "blast_radius": ("GET", "/api/v1/graph/blast-radius/{node_id}"),
        "centrality": ("GET", "/api/v1/graph/centrality/{node_id}"),
        "evidence": ("GET", "/api/v1/graph/evidence/{node_id}"),
        "investigation": ("GET", "/api/v1/graph/investigation/{investigation_id}"),
        "metadata": ("GET", "/api/v1/graph/metadata"),
        "statistics": ("GET", "/api/v1/graph/statistics"),
        "search": ("POST", "/api/v1/graph/search"),
        "relationships": ("POST", "/api/v1/graph/relationships/search"),
        "expand": ("POST", "/api/v1/graph/expand"),
        "subgraph": ("POST", "/api/v1/graph/subgraph"),
        "risk_propagation": ("POST", "/api/v1/graph/risk-propagation"),
    }

    def __init__(self, client: GraphServiceClient, *, endpoint_registry: EndpointRegistry | None = None, service_registry: ServiceRegistry | None = None):
        self._client = client
        self.service_registry = service_registry or ServiceRegistry({"graph": ServiceDefinition("graph", "")})
        self.endpoint_registry = endpoint_registry or EndpointRegistry([EndpointDefinition("graph", operation, method, path) for operation, (method, path) in self.ENDPOINTS.items()])

    def name(self) -> str:
        return "graph"

    def execute(self, state: InvestigationState, params: Dict[str, Any] | None = None) -> Dict[str, Any]:
        params = dict(params or {})
        operation = str(params.pop("operation", "expand"))
        correlation_id = params.pop("correlation_id", None) or state.investigation_id
        cancel_event = params.pop("cancel_event", None)
        if operation == "expand" and "node_id" not in params:
            evidence = state.evidence or params.get("evidence", [])
            first = evidence[0] if evidence else {}
            params["node_id"] = first.get("id") or first.get("evidence_id") or "account-001"
        params.pop("evidence", None)
        if operation == "investigation":
            params.setdefault("investigation_id", state.investigation_id)
        if operation not in self.ENDPOINTS:
            raise GraphToolError(f"unsupported graph operation: {operation}")
        try:
            endpoint = self.endpoint_registry.get("graph", operation)
            path = endpoint.path.format(**params)
            request_params = {key: value for key, value in params.items() if key not in {"node_id", "investigation_id", "source_id", "target_id"}}
            if endpoint.method == "GET":
                payload = self._client.get(path, params=request_params or None, cancel_event=cancel_event, correlation_id=correlation_id)
            else:
                payload = self._client.post(path, request=params, cancel_event=cancel_event, correlation_id=correlation_id)
            return dict(payload)
        except (KeyError, IntegrationException) as exc:
            raise GraphToolError(f"Graph Query Layer {operation} failed") from exc
