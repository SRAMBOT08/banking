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
    ServiceDefinition,
    ServiceRegistry,
    StructuredLogger,
    TimeoutConfig,
)

from .interfaces import MemoryTool
from ..state import InvestigationState


class InvestigationMemoryToolError(RuntimeError):
    """Raised when historical investigation intelligence cannot be retrieved."""


class InvestigationMemoryClient(Protocol):
    def get(self, path: str, *, params: Optional[Dict[str, Any]] = None, cancel_event: Any = None, correlation_id: str | None = None, **kwargs) -> Mapping[str, Any]: ...
    def post(self, path: str, request: Any = None, *, cancel_event: Any = None, correlation_id: str | None = None, **kwargs) -> Mapping[str, Any]: ...


class InvestigationMemoryHTTPClient(BaseQueryClient):
    """Transport-only client for the Investigation Memory Query API."""

    def __init__(self, base_url: str, *, timeout_seconds: float = 10.0, retry_policy: RetryPolicy | None = None, circuit_breaker: CircuitBreaker | None = None, client: Any = None):
        transport = HttpClient(
            base_url,
            timeout=TimeoutConfig(connect=timeout_seconds, read=timeout_seconds, write=timeout_seconds, pool=timeout_seconds),
            retry_policy=retry_policy or RetryPolicy(max_attempts=3),
            circuit_breaker=circuit_breaker or CircuitBreaker(),
            client=client,
        )
        super().__init__(
            "memory",
            transport,
            request_mapper=RequestMapper(function=lambda value: value),
            response_mapper=ResponseMapper(function=lambda value: value),
            logger=StructuredLogger("memory"),
        )

    @classmethod
    def from_settings(cls, settings: IntegrationSettings, *, authentication=None) -> BaseQueryClient:
        return ClientFactory(settings, authentication=authentication).create_query_client("memory")


class InvestigationMemoryToolAdapter(MemoryTool):
    """Translate Agent historical-intelligence requests to Memory Query API calls."""

    ENDPOINTS = {
        "lookup": ("GET", "/api/v1/memory/investigation/{investigation_id}"),
        "similar": ("GET", "/api/v1/memory/similar/{investigation_id}"),
        "timeline": ("GET", "/api/v1/memory/timeline/{entity_id}"),
        "statistics": ("GET", "/api/v1/memory/statistics"),
        "metadata": ("GET", "/api/v1/memory/metadata"),
        "outcome": ("GET", "/api/v1/memory/outcome/{investigation_id}"),
        "resolution": ("GET", "/api/v1/memory/resolution/{investigation_id}"),
        "lessons": ("GET", "/api/v1/memory/lessons/{investigation_id}"),
        "related": ("GET", "/api/v1/memory/related/{investigation_id}"),
        "evidence": ("GET", "/api/v1/memory/evidence/{investigation_id}"),
        "threat": ("GET", "/api/v1/memory/threat/{investigation_id}"),
        "knowledge": ("GET", "/api/v1/memory/knowledge/{investigation_id}"),
        "graph": ("GET", "/api/v1/memory/graph/{investigation_id}"),
        "search": ("POST", "/api/v1/memory/search"),
        "similarity": ("POST", "/api/v1/memory/similarity"),
    }

    def __init__(self, client: InvestigationMemoryClient, *, endpoint_registry: EndpointRegistry | None = None, service_registry: ServiceRegistry | None = None):
        self._client = client
        self.service_registry = service_registry or ServiceRegistry({"memory": ServiceDefinition("memory", "")})
        self.endpoint_registry = endpoint_registry or EndpointRegistry([EndpointDefinition("memory", operation, method, path) for operation, (method, path) in self.ENDPOINTS.items()])

    def name(self) -> str:
        return "memory"

    @staticmethod
    def _historical_request(state: InvestigationState, params: Dict[str, Any]) -> Dict[str, Any]:
        evidence_types = [item.get("evidence_type", item.get("type", "")) for item in state.evidence]
        threat_patterns = [item.get("pattern_name", item.get("name", item.get("id", ""))) for item in state.matched_patterns or state.candidate_patterns]
        knowledge_references = [item.get("id", "") for item in state.knowledge.get("items", [])] if isinstance(state.knowledge, dict) else []
        graph_references = [item.get("id", "") for item in state.graph_results.get("nodes", [])] if isinstance(state.graph_results, dict) else []
        request = {
            "investigation_id": state.investigation_id,
            "tenant_id": state.tenant_id,
            "evidence_types": [item for item in evidence_types if item],
            "threat_patterns": [item for item in threat_patterns if item],
            "knowledge_references": [item for item in knowledge_references if item],
            "graph_references": [item for item in graph_references if item],
            "mitre_mapping": params.get("mitre_mapping", []),
            "fraud_category": params.get("fraud_category"),
            "risk_score": params.get("risk_score"),
            "confidence": state.final_confidence,
            "limit": params.get("limit", 10),
        }
        request.update({key: value for key, value in params.items() if key not in {"operation", "cancel_event", "correlation_id"}})
        return request

    def execute(self, state: InvestigationState, params: Dict[str, Any] | None = None) -> Dict[str, Any]:
        params = dict(params or {})
        operation = str(params.pop("operation", "search"))
        correlation_id = params.pop("correlation_id", None) or state.investigation_id
        cancel_event = params.pop("cancel_event", None)
        if operation not in self.ENDPOINTS:
            raise InvestigationMemoryToolError(f"unsupported memory operation: {operation}")
        try:
            endpoint = self.endpoint_registry.get("memory", operation)
            request = self._historical_request(state, params)
            if operation in {"lookup", "similar", "outcome", "resolution", "lessons", "related", "evidence", "threat", "knowledge", "graph"}:
                request_id = str(params.get("investigation_id", state.investigation_id))
                path = endpoint.path.format(investigation_id=request_id)
                query = {key: value for key, value in params.items() if key not in {"investigation_id"}}
                payload = self._client.get(path, params=query or None, cancel_event=cancel_event, correlation_id=correlation_id)
            elif operation == "timeline":
                entity_id = str(params.get("entity_id", state.investigation_id))
                path = endpoint.path.format(entity_id=entity_id)
                payload = self._client.get(path, params={"timeline_type": params.get("timeline_type", "entity")}, cancel_event=cancel_event, correlation_id=correlation_id)
            elif operation in {"statistics", "metadata"}:
                payload = self._client.get(endpoint.path, cancel_event=cancel_event, correlation_id=correlation_id)
            else:
                payload = self._client.post(endpoint.path, request=request, cancel_event=cancel_event, correlation_id=correlation_id)
            return dict(payload)
        except (KeyError, IntegrationException) as exc:
            raise InvestigationMemoryToolError(f"Investigation Memory Query Layer {operation} failed") from exc
