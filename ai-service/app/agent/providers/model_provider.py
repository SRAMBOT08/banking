from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Dict, Any


class ModelProvider(ABC):
    """Abstract provider for ML model access through configured backends (NIM, etc.).

    The Agent talks to ModelProvider only; the provider is responsible for integrating
    with NIM or other model orchestration layers.
    """

    @abstractmethod
    def generate(self, prompt: str, params: Dict[str, Any]) -> str:
        raise NotImplementedError()
