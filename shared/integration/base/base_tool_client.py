from __future__ import annotations
from typing import Any, Mapping
from ..mapping import RequestMapper, ResponseMapper, validate_request
from ..observability import StructuredLogger
from ..transport import HttpClient


class BaseToolClient:
    """Common client boundary for Agent Tool Adapters."""

    def __init__(self, service: str, transport: HttpClient, *, request_mapper: RequestMapper | None = None, response_mapper: ResponseMapper | None = None, logger: StructuredLogger | None = None):
        self.service = service
        self.transport = transport
        self.request_mapper = request_mapper
        self.response_mapper = response_mapper
        self.logger = logger or StructuredLogger(service)

    def request(self, method: str, path: str, *, request: Any = None, request_model=None, response_mapper: ResponseMapper | None = None, cancel_event: Any = None, correlation_id: str | None = None, **kwargs) -> Any:
        mapped_request = self.request_mapper.map(request) if self.request_mapper else request
        mapped_request = validate_request(mapped_request, request_model)
        started = self.logger.timer()
        self.logger.request(method=method, endpoint=path, correlation_id=correlation_id)
        try:
            payload = self.transport.request(method, path, json=mapped_request, cancel_event=cancel_event, correlation_id=correlation_id, **kwargs)
            self.logger.response(method=method, endpoint=path, latency_ms=(self.logger.timer() - started) * 1000, correlation_id=correlation_id)
            mapper = response_mapper or self.response_mapper
            return mapper.map(payload) if mapper else payload
        except Exception as exc:
            self.logger.error(method=method, endpoint=path, exception=exc, correlation_id=correlation_id)
            raise

    def execute(self, operation: Any, request: dict[str, Any], cancel_event: Any = None) -> Mapping[str, Any]:
        raise NotImplementedError("service clients define operation endpoints and mappings")

    def close(self) -> None:
        self.transport.close()
