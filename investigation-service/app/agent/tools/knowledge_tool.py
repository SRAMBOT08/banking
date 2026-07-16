from __future__ import annotations

from typing import Any, Dict, Mapping, Optional, Protocol

from shared.integration import BaseQueryClient, CircuitBreaker, IntegrationException, RetryPolicy, HttpClient, TimeoutConfig
from .interfaces import KnowledgeTool
from ..state import InvestigationState


class KnowledgeToolError(RuntimeError):
    """Raised when the Knowledge Query Layer cannot answer a query."""


class KnowledgeServiceClient(Protocol):
    def search(self, path: str, request: Any = None, *, cancel_event: Any = None, **kwargs) -> Mapping[str, Any]: ...
    def get(self, path: str, *, params: Optional[Dict[str, Any]] = None, cancel_event: Any = None, **kwargs) -> Mapping[str, Any]: ...


class KnowledgeServiceHTTPClient(BaseQueryClient):
    """SDK-backed transport client for the Knowledge Query API."""

    def __init__(self, base_url: str, *, timeout_seconds: float = 10.0, retry_policy: RetryPolicy | None = None, circuit_breaker: CircuitBreaker | None = None, client: Any = None):
        transport = HttpClient(
            base_url,
            timeout=TimeoutConfig(connect=timeout_seconds, read=timeout_seconds, write=timeout_seconds, pool=timeout_seconds),
            retry_policy=retry_policy or RetryPolicy(max_attempts=3),
            client=client,
            circuit_breaker=circuit_breaker,
        )
        super().__init__("knowledge", transport)


class KnowledgeToolAdapter(KnowledgeTool):
    """Thin Agent-to-Knowledge Query API translation layer."""

    ENDPOINTS = {
        "item": "/api/v1/knowledge/{id}",
        "pattern": "/api/v1/knowledge/pattern/{id}",
        "technique": "/api/v1/knowledge/mitre/technique/{id}",
        "tactic": "/api/v1/knowledge/mitre/tactic/{id}",
        "playbook": "/api/v1/knowledge/playbook/{id}",
        "fraud": "/api/v1/knowledge/fraud/{id}",
        "control": "/api/v1/knowledge/control/{id}",
        "recommendation": "/api/v1/knowledge/recommendation/{id}",
        "detection": "/api/v1/knowledge/detection/{id}",
        "indicator": "/api/v1/knowledge/indicator/{id}",
        "quantum": "/api/v1/knowledge/quantum/{id}",
        "relationship": "/api/v1/knowledge/relationship/{id}",
        "version": "/api/v1/knowledge/version/{id}",
        "metadata": "/api/v1/knowledge/metadata",
        "statistics": "/api/v1/knowledge/statistics",
        "validation": "/api/v1/knowledge/validation",
        "search": "/api/v1/knowledge/search",
        "similar": "/api/v1/knowledge/similar/{id}",
    }

    def __init__(self, client: KnowledgeServiceClient):
        self._client = client

    def name(self) -> str:
        return "knowledge"

    def execute(self, state: InvestigationState, query: Dict[str, Any]) -> Any:
        # Hypothesis generation supplies matched patterns rather than an explicit
        # operation.  Preserve that node's list contract while retrieval keeps the
        # full search envelope for state.knowledge.
        pattern_mode = "patterns" in query and "operation" not in query
        operation = str(query.get("operation", "search"))
        cancel_event = query.get("cancel_event")
        try:
            if operation == "search":
                request = {key: value for key, value in query.items() if key not in {"operation", "cancel_event"}}
                request.setdefault("tenant_id", state.tenant_id)
                request.setdefault("investigation_id", state.investigation_id)
                payload = dict(self._client.search(self.ENDPOINTS[operation], request, cancel_event=cancel_event))
                return payload.get("items", []) if pattern_mode else payload
            if operation == "similar":
                path = self.ENDPOINTS[operation].format(id=query["id"])
                return dict(self._client.get(path, params={"limit": query.get("limit", 10)}, cancel_event=cancel_event))
            if operation in {"metadata", "statistics", "validation"}:
                return dict(self._client.get(self.ENDPOINTS[operation], cancel_event=cancel_event))
            if operation == "relationships":
                path = f"/api/v1/knowledge/relationship/item/{query['id']}"
                return dict(self._client.get(path, cancel_event=cancel_event))
            path = self.ENDPOINTS[operation].format(id=query["id"])
            return dict(self._client.get(path, cancel_event=cancel_event))
        except (KeyError, IntegrationException) as exc:
            raise KnowledgeToolError(f"Knowledge Query Layer {operation} failed") from exc
