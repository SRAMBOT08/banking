from __future__ import annotations

import hashlib
import json
from abc import ABC, abstractmethod
from typing import Optional

import redis.asyncio as redis


class DedupeStore(ABC):
    @abstractmethod
    async def check_and_set(self, key: str, ttl_seconds: int) -> bool:
        """Return True if key already existed (duplicate), False otherwise."""


class RedisDedupeStore(DedupeStore):
    def __init__(self, redis_url: str):
        # redis.asyncio exposes the same high-level API as redis-py but async
        self._redis: redis.Redis = redis.from_url(redis_url)

    async def check_and_set(self, key: str, ttl_seconds: int) -> bool:
        # SET key with NX and expiry; returns True if key was set (i.e. NOT a duplicate).
        was_set = await self._redis.set(key, "1", ex=ttl_seconds, nx=True)
        # Convert Redis truthy value to boolean: True means we created the key (not duplicate)
        return not bool(was_set)


class InMemoryDedupeStore(DedupeStore):
    def __init__(self):
        self._store = {}

    async def check_and_set(self, key: str, ttl_seconds: int) -> bool:
        import time

        now = int(time.time())
        if key in self._store and self._store[key] > now:
            return True
        self._store[key] = now + ttl_seconds
        return False


def deterministic_checksum(payload: dict, stable_metadata: Optional[dict] = None) -> str:
    payload_bytes = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    meta_bytes = b""
    if stable_metadata:
        meta_bytes = json.dumps(stable_metadata, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    h = hashlib.sha256()
    h.update(payload_bytes)
    h.update(b"::")
    h.update(meta_bytes)
    return h.hexdigest()
