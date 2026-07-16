from __future__ import annotations
from typing import Any
from .models import ProvenanceReference


class ProvenanceManager:
    """Maps aggregator provenance to immutable case references."""
    DEFAULTS = {
        'evidence': 'evidence-intelligence-service',
        'threat': 'threat-intelligence-service',
        'knowledge': 'knowledge-service',
        'graph': 'graph-intelligence-service',
        'historical': 'investigation-memory-service',
        'memory': 'investigation-memory-service',
    }

    def from_context(self, context: Any) -> tuple[ProvenanceReference, ...]:
        raw = getattr(context, 'provenance', None)
        if raw is None and isinstance(context, dict): raw = context.get('provenance', [])
        result = []
        for item in raw or []:
            data = item.model_dump(mode='python') if hasattr(item, 'model_dump') else dict(item)
            service = data.get('originating_service') or self.DEFAULTS.get(data.get('fact_type', ''), 'investigation-context')
            result.append(ProvenanceReference(source_service=service, source_id=data.get('source_id'), source_version=data.get('version'), source_path=data.get('fact_type'), originating_at=data.get('query_time'), correlation_id=data.get('correlation_id'), investigation_id=data.get('investigation_id')))
        return tuple(result)

    def for_section(self, provenance: tuple[ProvenanceReference, ...], source: str) -> tuple[ProvenanceReference, ...]:
        return tuple(item for item in provenance if source in item.source_service or item.source_service == source)
