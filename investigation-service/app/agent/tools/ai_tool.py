from __future__ import annotations
from typing import Dict, Any
from .interfaces import AITool


class AIToolAdapter(AITool):
    def __init__(self, config: Dict[str, Any]):
        self.config = config

    def name(self) -> str:
        return "ai_tool"

    def execute(self, state, prompt: str) -> str:
        raise NotImplementedError("AIToolAdapter requires a concrete AI Service adapter")
