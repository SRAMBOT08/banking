from __future__ import annotations
from typing import Dict, Any
from .model_provider import ModelProvider


class NIMProvider(ModelProvider):
    def __init__(self, config: Dict[str, Any]):
        self.config = config

    def generate(self, prompt: str, params: Dict[str, Any]) -> str:
        raise NotImplementedError("NIMProvider requires an explicitly configured model integration")
