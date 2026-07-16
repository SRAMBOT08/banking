from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any
from ..models import AdapterOperation, ExecutionAction


class AdapterResult(dict): pass


class ExecutionAdapter(ABC):
    @abstractmethod
    async def execute(self, execution_id: str, action: ExecutionAction) -> AdapterResult: ...
    @abstractmethod
    def supports(self, operation: AdapterOperation) -> bool: ...
