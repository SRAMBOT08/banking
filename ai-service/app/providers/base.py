from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, Dict
from app.schemas.provider import ProviderResponse


class BaseLLMProvider(ABC):
    """Stable strategy interface; reasoning code never depends on a vendor SDK."""

    @property
    @abstractmethod
    def model_name(self) -> str:
        raise NotImplementedError

    @abstractmethod
    async def complete(self, prompt: str, *, system_prompt: str = "", metadata: Dict[str, Any] | None = None) -> ProviderResponse:
        raise NotImplementedError

    def estimate_tokens(self, text: str) -> int:
        return max(1, len(text) // 4)

    def estimate_cost(self, prompt_tokens: int, completion_tokens: int) -> float:
        return 0.0
