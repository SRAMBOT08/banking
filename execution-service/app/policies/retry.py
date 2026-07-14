from __future__ import annotations

from app.models import ExecutionTask
from app.policies.base import RetryPolicy


class DeterministicRetryPolicy(RetryPolicy):
    name = "deterministic_retry_policy"

    def should_retry(self, task: ExecutionTask) -> bool:
        return task.retry_count < task.max_retries
