from __future__ import annotations
from typing import Any, Dict
from app.models.context import AIContext
from app.models.snapshot_contract import SnapshotDocument
from app.prompting.builder import PromptBuilder
from app.reasoning.engine import ReasoningEngine, ReasoningRequest
from app.schemas.api import AIResponse
from app.services.cache import InMemoryCache
from app.services.context_loader import SnapshotContextLoader
from app.services.metrics import AIMetrics
from app.memory.conversation import ConversationMemory
from app.validation.response_validator import ResponseValidationError
from app.config.settings import Settings


class AIInvestigationService:
    def __init__(self, context_loader: SnapshotContextLoader, prompt_builder: PromptBuilder,
                 reasoning_engine: ReasoningEngine, conversation: ConversationMemory,
                 metrics: AIMetrics, cache: InMemoryCache, settings: Settings):
        self.context_loader = context_loader
        self.prompt_builder = prompt_builder
        self.reasoning_engine = reasoning_engine
        self.conversation = conversation
        self.metrics = metrics
        self.cache = cache
        self.settings = settings

    def context(self, snapshot: Dict[str, Any] | SnapshotDocument) -> AIContext:
        key = (str(snapshot.get("metadata", {}).get("snapshot_id")) if isinstance(snapshot, dict) else snapshot.metadata["snapshot_id"])
        cached = self.cache.get(key)
        if cached is not None:
            return cached
        return self.cache.set(key, self.context_loader.load(snapshot))

    async def reason(self, snapshot: Dict[str, Any] | SnapshotDocument, reasoning_type: str, question: str | None = None) -> AIResponse:
        context = self.context(snapshot)
        try:
            response = await self.reasoning_engine.reason(ReasoningRequest(reasoning_type=reasoning_type, context=context, question=question))
        except ResponseValidationError:
            self.metrics.failure()
            raise
        usage = response.usage
        self.metrics.record(latency_ms=response.latency_ms, reasoning_time_ms=response.latency_ms,
                           tokens=usage.get("prompt_tokens", 0) + usage.get("completion_tokens", 0),
                           prompt_size=usage.get("prompt_tokens", 0), completion_size=usage.get("completion_tokens", 0),
                           cache_hits=self.cache.hits, cache_misses=self.cache.misses)
        conversation_key = str(context.investigation.get("investigation_id", context.snapshot_id))
        self.conversation.append(conversation_key,
                                 {"reasoning_type": reasoning_type, "snapshot_version": context.snapshot_version,
                                  "prompt_history": self.prompt_builder.build(context, reasoning_type, question),
                                  "response": response.model_dump(mode="json"), "model": response.model,
                                  "usage": usage, "latency_ms": response.latency_ms})
        return response
