from __future__ import annotations
import json
import time
from typing import Any, Dict
from pydantic import BaseModel
from app.models.context import AIContext
from app.prompting.builder import PromptBuilder
from app.providers.base import BaseLLMProvider
from app.schemas.api import AIResponse, Claim
from app.validation.response_validator import ResponseValidator


class ReasoningRequest(BaseModel):
    reasoning_type: str
    context: AIContext
    question: str | None = None


class ReasoningEngine:
    def __init__(self, provider: BaseLLMProvider, prompt_builder: PromptBuilder, validator: ResponseValidator):
        self.provider = provider
        self.prompt_builder = prompt_builder
        self.validator = validator

    async def reason(self, request: ReasoningRequest) -> AIResponse:
        started = time.perf_counter()
        prompt = self.prompt_builder.build(request.context, request.reasoning_type, request.question)
        provider_response = await self.provider.complete(prompt, metadata={"snapshot_id": request.context.snapshot_id})
        try:
            data: Dict[str, Any] = json.loads(provider_response.text)
        except json.JSONDecodeError as exc:
            raise ValueError("provider response was not valid JSON") from exc
        response = AIResponse(
            reasoning_type=request.reasoning_type,
            snapshot_id=request.context.snapshot_id,
            snapshot_version=request.context.snapshot_version,
            answer=str(data.get("answer", "")),
            claims=[Claim.model_validate(item) for item in data.get("claims", [])],
            recommendations=list(data.get("recommendations", [])),
            confidence=int(request.context.confidence.get("score", 0)),
            priority=request.context.priority,
            model=provider_response.model,
            usage={"prompt_tokens": provider_response.prompt_tokens, "completion_tokens": provider_response.completion_tokens},
            latency_ms=round((time.perf_counter() - started) * 1000, 3),
        )
        return self.validator.assert_valid(response, request.context)
