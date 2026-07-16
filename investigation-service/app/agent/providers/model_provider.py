from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Dict, Any


class ModelProvider(ABC):
    @abstractmethod
    def generate(self, prompt: str, params: Dict[str, Any]) -> str:
        raise NotImplementedError()
