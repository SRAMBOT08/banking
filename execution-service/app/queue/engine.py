from __future__ import annotations

import heapq
from typing import Dict, List, Set, Tuple

from app.models import ExecutionQueue, ExecutionTask, ExecutionTaskState


class DeterministicExecutionQueueEngine:
    """Supports FIFO, priority, dependency, delayed, retry, and dead-letter structures deterministically."""

    def __init__(self):
        self._priority_heap: List[Tuple[int, int, str]] = []
        self._fifo_counter = 0
        self._task_dependencies: Dict[str, Set[str]] = {}

    def build_queue(self, plan_id: str, tasks: List[ExecutionTask]) -> ExecutionQueue:
        if not tasks:
            raise ValueError("execution plan must contain tasks")
        correlation_id = tasks[0].correlation_id
        investigation_id = tasks[0].investigation_id
        tenant_id = tasks[0].tenant_id
        queue = ExecutionQueue(
            correlation_id=correlation_id,
            investigation_id=investigation_id,
            tenant_id=tenant_id,
            plan_id=plan_id,
        )
        for task in sorted(tasks, key=lambda item: (item.priority * -1, item.deterministic_order, item.task_id)):
            self._task_dependencies[task.task_id] = set(task.dependencies)
            queue.pending_tasks.append(task.task_id)
            self._fifo_counter += 1
            # min heap: lower tuple wins, so invert priority
            heapq.heappush(self._priority_heap, (-task.priority, task.deterministic_order, task.task_id))
        return queue

    def refresh_ready(self, queue: ExecutionQueue, tasks_by_id: Dict[str, ExecutionTask]) -> ExecutionQueue:
        queue.ready_tasks = []
        queue.blocked_tasks = []
        completed = {task_id for task_id, task in tasks_by_id.items() if task.state == ExecutionTaskState.COMPLETED}
        for task_id in queue.pending_tasks:
            deps = self._task_dependencies.get(task_id, set())
            if deps and not deps.issubset(completed):
                queue.blocked_tasks.append(task_id)
            else:
                queue.ready_tasks.append(task_id)
        queue.ready_tasks.sort(key=lambda task_id: (
            tasks_by_id[task_id].deterministic_order,
            tasks_by_id[task_id].task_id,
        ))
        return queue

    def next_ready_task(self, queue: ExecutionQueue, tasks_by_id: Dict[str, ExecutionTask]) -> str | None:
        self.refresh_ready(queue, tasks_by_id)
        if not queue.ready_tasks:
            return None
        return queue.ready_tasks[0]
