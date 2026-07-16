from __future__ import annotations

from typing import Any, Dict, List, Mapping, Optional, Protocol

from pydantic import BaseModel, Field
from shared.integration import BaseQueryClient, HttpClient, IntegrationException, RetryPolicy, TimeoutConfig

from .interfaces import ThreatTool
from ..state import InvestigationState

class ThreatToolError(RuntimeError):
    pass


class ThreatAgentCandidate(BaseModel):
    threat_id: str
    pattern_name: str
    pattern_version: str = "1.0"
    confidence: float = 0.0
    tenant_id: Optional[str] = None
    investigation_id: Optional[str] = None
    correlation_id: Optional[str] = None
    timestamp: Optional[str] = None
    explanation: Dict[str, Any] = Field(default_factory=dict)
    evidence_refs: List[Dict[str, Any]] = Field(default_factory=list)
    missing_evidence: List[Dict[str, Any]] = Field(default_factory=list)


class ThreatServiceClient(Protocol):
    def search(self, request: Dict[str, Any], cancel_event: Any = None) -> Mapping[str, Any]:
        ...

    def get(self, path: str, params: Optional[Dict[str, Any]] = None, cancel_event: Any = None) -> Mapping[str, Any]:
        ...


class ThreatServiceHTTPClient(BaseQueryClient):
    """Transport-only client for the Threat Intelligence Query Layer."""

    def __init__(self, base_url: str, timeout_seconds: float = 10.0, client: Optional[Any] = None):
        transport = HttpClient(base_url, timeout=TimeoutConfig(connect=timeout_seconds, read=timeout_seconds, write=timeout_seconds, pool=timeout_seconds), retry_policy=RetryPolicy(max_attempts=1), client=client)
        super().__init__("threat", transport)

    def search(self, request: Dict[str, Any], cancel_event: Any = None) -> Mapping[str, Any]:
        try:
            return super().search("/api/v1/threat/search", request=request, cancel_event=cancel_event)
        except IntegrationException as exc:
            raise ThreatToolError("Threat Query Layer search failed") from exc

    def close(self) -> None:
        super().close()


class ThreatToolAdapter(ThreatTool):
    def __init__(self, client: ThreatServiceClient):
        self._client = client

    def name(self) -> str:
        return "threat"

    @staticmethod
    def _request(state: InvestigationState, candidates: Any, params: Dict[str, Any]) -> Dict[str, Any]:
        request = {"tenant_id": state.tenant_id, "investigation_id": state.investigation_id, "evidence": candidates}
        request.update({key: value for key, value in params.items() if key != "cancel_event"})
        return request

    @staticmethod
    def _items(payload: Mapping[str, Any]) -> List[ThreatAgentCandidate]:
        raw_items = payload.get("items", payload.get("threats", payload.get("candidates", [])))
        return [ThreatAgentCandidate.model_validate(item) for item in raw_items]

    def execute(self, state: InvestigationState, candidates: List[Dict[str, Any]] | Dict[str, Any]) -> Any:
        params = candidates if isinstance(candidates, dict) else {}
        cancel_event = params.get("cancel_event")
        payload = self._client.search(self._request(state, candidates, params), cancel_event)
        items = self._items(payload)
        if params.get("missing_evidence_check"):
            return {"missing_evidence": [missing for item in items for missing in item.missing_evidence]}
        if "graph" in params or "patterns" in params:
            breakdown = payload.get("confidence_breakdown")
            if isinstance(breakdown, Mapping):
                return dict(breakdown)
            return {"pattern": max((item.confidence for item in items), default=0.0) / 100.0}
        result = [item.model_dump(mode="json") for item in items]
        return result
