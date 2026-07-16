from __future__ import annotations
from typing import Dict, Any
from .interfaces import ExecutionTool


class ExecutionToolAdapter(ExecutionTool):
    def __init__(self, config: Dict[str, Any]):
        self.config = config

    def name(self) -> str:
        return "execution_tool"

    def execute(self, state, params: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError("ExecutionToolAdapter requires a concrete Execution Service adapter")
