from __future__ import annotations

import asyncio
from dataclasses import dataclass

from app.models import RetryPolicy


@dataclass
class RetryState:
    attempt: int = 0
    open_circuit: bool = False


class RetryEngine:
    def __init__(self, policy: RetryPolicy):
        self.policy = policy

    def should_retry(self, status_code: int | None, error: Exception | None, state: RetryState) -> bool:
        if state.open_circuit:
            return False
        if state.attempt >= self.policy.max_retries:
            return False
        if status_code is not None and status_code in self.policy.retryable_status_codes:
            return True
        return error is not None

    async def backoff(self, state: RetryState) -> None:
        delay_ms = min(self.policy.max_delay_ms, self.policy.base_delay_ms * (2 ** state.attempt))
        await asyncio.sleep(delay_ms / 1000.0)
