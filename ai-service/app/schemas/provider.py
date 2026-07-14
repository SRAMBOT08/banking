from typing import Any, Dict
from pydantic import BaseModel, Field


class ProviderResponse(BaseModel):
    text: str
    model: str
    prompt_tokens: int = 0
    completion_tokens: int = 0
    latency_ms: float = 0.0
    metadata: Dict[str, Any] = Field(default_factory=dict)
