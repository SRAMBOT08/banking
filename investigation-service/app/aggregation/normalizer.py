from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Mapping


class IntelligenceNormalizer:
    """Normalize heterogeneous service payloads into deterministic dictionaries."""

    @staticmethod
    def as_items(payload: Any, keys: tuple[str, ...] = ()) -> list[dict[str, Any]]:
        if isinstance(payload, list):
            return [item if isinstance(item, dict) else {"value": item} for item in payload]
        if not isinstance(payload, Mapping):
            return []
        for key in keys + ("items", "evidence", "threats", "candidates", "patterns", "relationships", "nodes"):
            value = payload.get(key)
            if isinstance(value, list):
                return [item if isinstance(item, dict) else {"value": item} for item in value]
        return [dict(payload)] if payload else []

    @staticmethod
    def normalize_id(item: Mapping[str, Any]) -> str:
        return str(item.get("id") or item.get("evidence_id") or item.get("threat_id") or item.get("knowledge_id") or item.get("investigation_id") or item.get("relationship_id") or "")

    @staticmethod
    def normalize_confidence(value: Any) -> float | None:
        if value is None:
            return None
        score = float(value)
        return max(0.0, min(1.0, score / 100.0 if score > 1 else score))

    @staticmethod
    def normalize_timestamp(value: Any) -> str | None:
        if value is None:
            return None
        if isinstance(value, datetime):
            return value.astimezone(timezone.utc).isoformat()
        return str(value)

    def normalize_payload(self, payload: Any, source: str, keys: tuple[str, ...] = ()) -> tuple[list[dict[str, Any]], dict[str, Any]]:
        items = self.as_items(payload, keys)
        normalized = []
        for item in items:
            copy = dict(item)
            identifier = self.normalize_id(copy)
            if identifier:
                copy["id"] = identifier
            if "confidence" in copy:
                confidence = self.normalize_confidence(copy["confidence"])
                if confidence is not None:
                    copy["confidence"] = confidence
            if "timestamp" in copy:
                copy["timestamp"] = self.normalize_timestamp(copy["timestamp"])
            copy["source"] = source
            normalized.append(copy)
        raw = dict(payload) if isinstance(payload, Mapping) else {"items": normalized}
        return normalized, raw
