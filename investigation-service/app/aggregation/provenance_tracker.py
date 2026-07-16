from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from .models import DataProvenance


class ProvenanceTracker:
    def record(self, *, service: str, fact: dict[str, Any], investigation_id: str, correlation_id: str, workflow_id: str | None = None) -> DataProvenance:
        return DataProvenance(
            source_id=str(fact.get("source") or service),
            originating_service=service,
            repository=str(fact.get("repository", "unknown")),
            query_time=datetime.now(timezone.utc),
            version=str(fact.get("version", "v1")),
            correlation_id=correlation_id,
            investigation_id=investigation_id,
            workflow_id=workflow_id,
            confidence_source=service,
            fact_type=str(fact.get("type", service)),
            fact_id=str(fact.get("id") or fact.get("name") or "unknown"),
        )
