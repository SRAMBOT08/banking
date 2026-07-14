from __future__ import annotations
import asyncio
import time
from typing import Any, Dict
import httpx
from app.config.settings import Settings
from app.schemas.provider import ProviderResponse
from app.providers.base import BaseLLMProvider


class GeminiProvider(BaseLLMProvider):
    """Gemini transport only. No SentinelIQ business rules belong here."""

    def __init__(self, settings: Settings, client: httpx.AsyncClient | None = None):
        self.settings = settings
        self.client = client
        self._endpoint = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"

    @property
    def model_name(self) -> str:
        return self.settings.gemini_model

    async def complete(self, prompt: str, *, system_prompt: str = "", metadata: Dict[str, Any] | None = None) -> ProviderResponse:
        if not self.settings.gemini_api_key:
            raise RuntimeError("GEMINI_API_KEY is required for GeminiProvider")
        payload = {
            "systemInstruction": {"parts": [{"text": system_prompt}]} if system_prompt else None,
            "contents": [{"role": "user", "parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": self.settings.temperature,
                "topP": self.settings.top_p,
                "topK": self.settings.top_k,
                "maxOutputTokens": self.settings.max_tokens,
                "responseMimeType": "application/json",
            },
        }
        payload = {key: value for key, value in payload.items() if value is not None}
        url = self._endpoint.format(model=self.settings.gemini_model)
        headers = {"x-goog-api-key": self.settings.gemini_api_key}
        started = time.perf_counter()
        attempts = max(0, self.settings.retry_count) + 1
        last_error: Exception | None = None
        owns_client = self.client is None
        client = self.client or httpx.AsyncClient(timeout=self.settings.timeout_seconds)
        try:
            for attempt in range(attempts):
                try:
                    response = await client.post(url, headers=headers, json=payload)
                    response.raise_for_status()
                    data = response.json()
                    parts = data.get("candidates", [{}])[0].get("content", {}).get("parts", [])
                    text = "".join(str(part.get("text", "")) for part in parts)
                    prompt_tokens = int(data.get("usageMetadata", {}).get("promptTokenCount", self.estimate_tokens(prompt)))
                    completion_tokens = int(data.get("usageMetadata", {}).get("candidatesTokenCount", self.estimate_tokens(text)))
                    return ProviderResponse(text=text, model=self.model_name, prompt_tokens=prompt_tokens,
                                            completion_tokens=completion_tokens,
                                            latency_ms=round((time.perf_counter() - started) * 1000, 3),
                                            metadata={"attempt": attempt + 1, "streaming": self.settings.streaming})
                except Exception as exc:
                    last_error = exc
                    if attempt + 1 < attempts:
                        await asyncio.sleep(self.settings.retry_backoff_seconds * (attempt + 1))
            raise RuntimeError(f"Gemini request failed after {attempts} attempt(s): {last_error}") from last_error
        finally:
            if owns_client:
                await client.aclose()

    def estimate_cost(self, prompt_tokens: int, completion_tokens: int) -> float:
        # Cost is deliberately configurable later; zero avoids fabricated pricing.
        return 0.0
