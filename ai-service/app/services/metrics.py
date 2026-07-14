from __future__ import annotations
from threading import RLock
from typing import Any, Dict


class AIMetrics:
    def __init__(self):
        self._lock = RLock()
        self._values = {"requests": 0, "latency_ms": 0.0, "tokens": 0, "prompt_size": 0,
                        "completion_size": 0, "reasoning_time_ms": 0.0, "validation_failures": 0,
                        "retry_count": 0, "provider_errors": 0, "cache_hits": 0, "cache_misses": 0}

    def record(self, **values: Any) -> None:
        with self._lock:
            self._values["requests"] += 1
            for key, value in values.items():
                if key in self._values:
                    self._values[key] += value

    def failure(self) -> None:
        with self._lock:
            self._values["validation_failures"] += 1

    def provider_error(self) -> None:
        with self._lock:
            self._values["provider_errors"] += 1

    def snapshot(self) -> Dict[str, Any]:
        with self._lock:
            result = dict(self._values)
            requests = max(1, result["requests"])
            result["average_latency_ms"] = round(result["latency_ms"] / requests, 3)
            result["average_reasoning_time_ms"] = round(result["reasoning_time_ms"] / requests, 3)
            return result
