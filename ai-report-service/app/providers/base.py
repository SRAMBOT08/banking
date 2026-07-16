from __future__ import annotations
from abc import ABC, abstractmethod
from pydantic import BaseModel


class ProviderResponse(BaseModel):
    text: str
    model: str


class ModelProvider(ABC):
    @property
    @abstractmethod
    def model_name(self) -> str: ...
    @abstractmethod
    async def generate(self, prompt: str) -> ProviderResponse: ...
