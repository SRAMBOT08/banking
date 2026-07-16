from __future__ import annotations
from enum import Enum
from typing import Any, Dict, List, Mapping, Optional, Protocol

from pydantic import BaseModel, Field
from shared.integration import BaseToolClient, HttpClient, IntegrationException, RetryPolicy, TimeoutConfig

from .interfaces import EvidenceTool
from ..state import InvestigationState

class EvidenceToolError(RuntimeError):
    """Raised when the Evidence Intelligence Service cannot fulfill a request."""


class EvidenceOperation(str, Enum):
    COLLECT = "collect"
    RESOLVE_ENTITIES = "resolve_entities"
    RETRIEVE = "retrieve"
    RELATIONSHIPS = "relationships"
    METADATA = "metadata"
    VALIDATE = "validate"


class EvidenceItem(BaseModel):
    evidence_id: str
    evidence_type: str = "unknown"
    timestamp: Optional[str] = None
    confidence: float = 0.0
    properties: Dict[str, Any] = Field(default_factory=dict)
    source: str = "unknown"


class ResolvedEntity(BaseModel):
    entity_type: str
    canonical_id: str
    attributes: Dict[str, Any] = Field(default_factory=dict)


class EvidenceRelationship(BaseModel):
    source_id: str
    target_id: str
    relationship_type: str
    properties: Dict[str, Any] = Field(default_factory=dict)


class EvidenceMetadata(BaseModel):
    total: int = 0
    by_type: Dict[str, int] = Field(default_factory=dict)
    source_count: int = 0
    service_version: Optional[str] = None


class EvidenceValidation(BaseModel):
    valid: bool
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)


class EvidenceServiceResponse(BaseModel):
    evidence: List[EvidenceItem] = Field(default_factory=list)
    entities: List[ResolvedEntity] = Field(default_factory=list)
    relationships: List[EvidenceRelationship] = Field(default_factory=list)
    metadata: EvidenceMetadata = Field(default_factory=EvidenceMetadata)
    validation: Optional[EvidenceValidation] = None
    missing_evidence: List[Dict[str, Any]] = Field(default_factory=list)


class EvidenceServiceClient(Protocol):
    """Request/response boundary owned by the Evidence Intelligence Service."""

    def execute(self, operation: EvidenceOperation, request: Dict[str, Any], cancel_event: Any = None) -> Mapping[str, Any]:
        ...


class EvidenceServiceHTTPClient(BaseToolClient):
    """HTTP transport for the Evidence Service operation contract.

    The service URL and endpoint paths are injected so deployment-specific routing
    stays outside the Agent. This class performs transport only; extraction,
    resolution, correlation, and graph logic remain service responsibilities.
    """

    DEFAULT_PATHS = {
        EvidenceOperation.COLLECT: "/api/v1/evidence/search",
        EvidenceOperation.RESOLVE_ENTITIES: "/api/v1/evidence/entity/{entity_id}",
        EvidenceOperation.RETRIEVE: "/api/v1/evidence/search",
        EvidenceOperation.RELATIONSHIPS: "/api/v1/evidence/{evidence_id}/relationships",
        EvidenceOperation.METADATA: "/api/v1/evidence/{evidence_id}/metadata",
        EvidenceOperation.VALIDATE: "/api/v1/evidence/{evidence_id}/validation",
    }

    def __init__(self, base_url: str, timeout_seconds: float = 10.0, paths: Optional[Mapping[EvidenceOperation, str]] = None, client: Optional[Any] = None):
        self._base_url = base_url.rstrip("/")
        self._timeout_seconds = timeout_seconds
        self._paths = {**self.DEFAULT_PATHS, **(paths or {})}
        transport = HttpClient(base_url, timeout=TimeoutConfig(connect=timeout_seconds, read=timeout_seconds, write=timeout_seconds, pool=timeout_seconds), retry_policy=RetryPolicy(max_attempts=1), client=client)
        super().__init__("evidence", transport)

    def execute(self, operation: EvidenceOperation, request: Dict[str, Any], cancel_event: Any = None) -> Mapping[str, Any]:
        parameters = dict(request.get("parameters", {}))
        try:
            path = self._paths[operation].format(**{**request, **parameters})
            if operation is EvidenceOperation.RETRIEVE and parameters.get("evidence_id"):
                path = f"/api/v1/evidence/{parameters['evidence_id']}"
            if operation in {EvidenceOperation.COLLECT, EvidenceOperation.RETRIEVE}:
                query = {key: value for key, value in {**request, **parameters}.items() if key not in {"parameters", "evidence", "metadata", "tenant_id"}}
                payload = self.request("POST", path, request=query, cancel_event=cancel_event)
            else:
                payload = self.request("GET", path, params=parameters, cancel_event=cancel_event)
        except IntegrationException as exc:
            raise EvidenceToolError(f"Evidence Service {operation.value} failed") from exc
        if operation in {EvidenceOperation.COLLECT, EvidenceOperation.RETRIEVE}:
            if operation is EvidenceOperation.RETRIEVE and payload.get("evidence_id"):
                return {"evidence": [payload], "metadata": {"total": 1}}
            return {"evidence": payload.get("items", []), "metadata": {"total": payload.get("total", 0)}}
        if operation is EvidenceOperation.RESOLVE_ENTITIES:
            return {"entities": [{"entity_type": payload.get("entity_type", (payload.get("labels") or ["unknown"])[0]), "canonical_id": payload.get("entity_id"), "attributes": payload.get("attributes", {})}]}
        if operation is EvidenceOperation.RELATIONSHIPS:
            return {"relationships": payload.get("relationships", [])}
        if operation is EvidenceOperation.METADATA:
            return {"metadata": {"total": 1, "by_type": {payload.get("evidence_type", "unknown"): 1}, "source_count": 1}}
        if operation is EvidenceOperation.VALIDATE:
            return {"validation": payload}
        return payload

    def close(self) -> None:
        super().close()


class EvidenceToolAdapter(EvidenceTool):
    def __init__(self, client: EvidenceServiceClient):
        self._client = client

    def name(self) -> str:
        return "evidence"

    def execute(self, state: InvestigationState, params: Dict[str, Any]) -> Dict[str, Any]:
        operation = EvidenceOperation(params.get("operation", EvidenceOperation.COLLECT))
        request = {
            "investigation_id": state.investigation_id,
            "tenant_id": state.tenant_id,
            "evidence": state.evidence,
            "metadata": state.metadata,
            "parameters": {key: value for key, value in params.items() if key not in {"operation", "cancel_event"}},
        }
        payload = self._client.execute(operation, request, params.get("cancel_event"))
        result = EvidenceServiceResponse.model_validate(payload)
        mapped = result.model_dump(mode="json")
        return mapped
