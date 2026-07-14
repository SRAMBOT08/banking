from __future__ import annotations
import json
from typing import Any, Dict
from app.providers.base import BaseLLMProvider
from app.schemas.provider import ProviderResponse


class MockLLMProvider(BaseLLMProvider):
    """Offline provider used by tests and local development."""

    def __init__(self, model: str = "mock-deterministic"):
        self._model = model
        self.calls = 0

    @property
    def model_name(self) -> str:
        return self._model

    async def complete(self, prompt: str, *, system_prompt: str = "", metadata: Dict[str, Any] | None = None) -> ProviderResponse:
        self.calls += 1
        # PromptBuilder intentionally wraps canonical JSON in instructions. The
        # mock extracts that JSON without depending on any vendor behavior.
        start = prompt.find("{")
        if start < 0:
            raise ValueError("mock provider prompt does not contain context JSON")
        data = json.loads(prompt[start:])
        context = data["context"]
        snapshot_id = context["snapshot_id"]
        evidence = context.get("evidence", [])
        source_ids = [str(item.get("evidence_id")) for item in evidence if item.get("evidence_id")]
        claims = [{"text": f"Investigation {context['investigation'].get('investigation_id', snapshot_id)} contains {len(evidence)} evidence item(s).", "source_ids": source_ids}]
        result = {
            "answer": f"Snapshot {snapshot_id} supports a deterministic investigation summary.",
            "claims": claims,
            "recommendations": context.get("recommendations", []),
        }
        text = json.dumps(result, sort_keys=True)
        return ProviderResponse(text=text, model=self.model_name, prompt_tokens=self.estimate_tokens(prompt), completion_tokens=self.estimate_tokens(text))
