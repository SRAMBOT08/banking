from __future__ import annotations

from typing import Any
from .models import ConfidenceSource
from .normalizer import IntelligenceNormalizer


class ConfidenceTracker:
    """Records confidence supplied by sources; it never calculates final confidence."""

    def record(self, service: str, items: list[dict[str, Any]]) -> ConfidenceSource:
        values = [IntelligenceNormalizer.normalize_confidence(item.get("confidence")) for item in items]
        values = [value for value in values if value is not None]
        return ConfidenceSource(source=service, score=(sum(values) / len(values) if values else None), evidence_count=len(items))
