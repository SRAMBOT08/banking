from __future__ import annotations

from app.models import ExecutionTask, ExecutionTaskState
from app.policies.base import RollbackPolicy


class DeterministicRollbackPolicy(RollbackPolicy):
    name = "deterministic_rollback_policy"

    def should_rollback(self, task: ExecutionTask) -> bool:
        return task.state == ExecutionTaskState.FAILED and task.retry_count >= task.max_retries
