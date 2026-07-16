from __future__ import annotations
from .graph import GraphBuilder
from .tool_router import ToolRouter


class InvestigationPlanner:
    def __init__(self, router: ToolRouter):
        self.router = router

    def build(self) -> GraphBuilder:
        return GraphBuilder(self.router)
