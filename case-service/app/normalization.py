from __future__ import annotations
from typing import Any


class CaseNormalizer:
    """Normalize context values without enriching or interpreting them."""
    def items(self, value: Any) -> tuple[dict[str, Any], ...]:
        if isinstance(value, dict):
            value = value.get('items', value.get('patterns', value.get('relationships', [])))
        if not isinstance(value, list): return ()
        return tuple(dict(item) if isinstance(item, dict) else {'value': item} for item in value)

    def text(self, value: Any) -> str:
        return '' if value is None else str(value)

    def section(self, context: Any, name: str) -> dict[str, Any]:
        value = getattr(context, name, None)
        if value is None and isinstance(context, dict): value = context.get(name, {})
        if hasattr(value, 'model_dump'): value = value.model_dump(mode='python')
        return value if isinstance(value, dict) else {}
