from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Dict, List

from app.models import ApprovalDecision, ExecutionPlan, ExecutionTask, PolicyDecision


class ExecutionPolicy(ABC):
    name: str = "execution_policy"

    @abstractmethod
    def evaluate(self, plan: ExecutionPlan, task: ExecutionTask) -> PolicyDecision:
        raise NotImplementedError


class ApprovalPolicy(ABC):
    name: str = "approval_policy"

    @abstractmethod
    def evaluate(self, plan: ExecutionPlan, task: ExecutionTask) -> ApprovalDecision:
        raise NotImplementedError


class SchedulingPolicy(ABC):
    name: str = "scheduling_policy"

    @abstractmethod
    def sort_tasks(self, tasks: List[ExecutionTask]) -> List[ExecutionTask]:
        raise NotImplementedError


class RetryPolicy(ABC):
    name: str = "retry_policy"

    @abstractmethod
    def should_retry(self, task: ExecutionTask) -> bool:
        raise NotImplementedError


class RollbackPolicy(ABC):
    name: str = "rollback_policy"

    @abstractmethod
    def should_rollback(self, task: ExecutionTask) -> bool:
        raise NotImplementedError
