from __future__ import annotations
from typing import Optional
from .graph import GraphBuilder
from .tool_router import ToolRouter
from langgraph.checkpoint.postgres import PostgresSaver


class InvestigationPlanner:
    def __init__(self, router: ToolRouter, checkpointer: Optional[PostgresSaver] = None):
        self.router = router
        self._checkpointer = checkpointer

    def build(self) -> GraphBuilder:
        return GraphBuilder(self.router, checkpointer=self._checkpointer)
