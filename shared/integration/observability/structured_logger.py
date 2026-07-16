from __future__ import annotations
import logging
from time import perf_counter


class StructuredLogger:
    def __init__(self, service: str, logger: logging.Logger | None = None):
        self.service = service
        self.logger = logger or logging.getLogger(f"sentineliq.integration.{service}")

    def request(self, *, method: str, endpoint: str, correlation_id: str | None = None, investigation_id: str | None = None, workflow_id: str | None = None, **extra):
        self.logger.info({"event": "integration_request", "service": self.service, "method": method, "endpoint": endpoint, "correlation_id": correlation_id, "investigation_id": investigation_id, "workflow_id": workflow_id, **extra})

    def response(self, *, method: str, endpoint: str, status_code: int | None = None, latency_ms: float | None = None, retry_count: int = 0, correlation_id: str | None = None, **extra):
        self.logger.info({"event": "integration_response", "service": self.service, "method": method, "endpoint": endpoint, "status_code": status_code, "latency_ms": latency_ms, "retry_count": retry_count, "correlation_id": correlation_id, **extra})

    def error(self, *, method: str, endpoint: str, exception: BaseException, correlation_id: str | None = None, **extra):
        self.logger.error({"event": "integration_error", "service": self.service, "method": method, "endpoint": endpoint, "exception": str(exception), "correlation_id": correlation_id, **extra})

    def timer(self):
        return perf_counter()
