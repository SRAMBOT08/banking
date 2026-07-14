import pytest
from app.config.settings import Settings
from app.memory.conversation import ConversationMemory
from app.prompting.builder import PromptBuilder
from app.providers.mock import MockLLMProvider
from app.reasoning.engine import ReasoningEngine
from app.services.ai_service import AIInvestigationService
from app.services.cache import InMemoryCache
from app.services.context_loader import SnapshotContextLoader
from app.services.metrics import AIMetrics
from app.validation.response_validator import ResponseValidator


@pytest.mark.asyncio
async def test_service_records_ai_only_history_and_metrics(snapshot_payload):
    provider = MockLLMProvider()
    service = AIInvestigationService(
        SnapshotContextLoader(), PromptBuilder(),
        ReasoningEngine(provider, PromptBuilder(), ResponseValidator()),
        ConversationMemory(), AIMetrics(), InMemoryCache(), Settings(kafka_bootstrap=""),
    )
    response = await service.reason(snapshot_payload, "executive_summary")
    assert response.snapshot_version == 1
    assert service.conversation.list("inv-1")[0]["snapshot_version"] == 1
    assert service.metrics.snapshot()["requests"] == 1
