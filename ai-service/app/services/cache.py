from __future__ import annotations
from typing import Any, Dict, Hashable


class InMemoryCache:
    def __init__(self):
        self._items: Dict[Hashable, Any] = {}
        self.hits = 0
        self.misses = 0

    def get(self, key: Hashable):
        if key in self._items:
            self.hits += 1
            return self._items[key]
        self.misses += 1
        return None

    def set(self, key: Hashable, value: Any) -> Any:
        self._items[key] = value
        return value
