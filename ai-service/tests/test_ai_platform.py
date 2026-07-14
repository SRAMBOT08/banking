import json
import pytest
from app.models.context import AIContext
from app.models.snapshot_contract import SnapshotDocument
from app.prompting.builder import PromptBuilder
from app.providers.mock import MockLLMProvider
from app.reasoning.engine import ReasoningEngine, ReasoningRequest
from app.services.context_loader import SnapshotContextLoader
from app.services.recommendations import RecommendationGenerator
from app.validation.response_validator import ResponseValidationError, ResponseValidator
from app.schemas.api import AIResponse, Claim


def test_context_loader_is_snapshot_only_and_context_is_frozen(snapshot_payload):
    context = SnapshotContextLoader().load(snapshot_payload)
    assert isinstance(context, AIContext)
    assert context.snapshot_id == "snap-1"
    assert context.graph_summary["node_count"] == 1
    with pytest.raises(Exception):
        context.priority = "LOW"


def test_prompt_builder_is_deterministic(snapshot_payload):
    context = SnapshotContextLoader().load(snapshot_payload)
    builder = PromptBuilder()
    assert builder.build(context, "executive_summary") == builder.build(context, "executive_summary")


@pytest.mark.asyncio
async def test_snapshot_to_mock_provider_to_validator(snapshot_payload):
    context = SnapshotContextLoader().load(snapshot_payload)
    engine = ReasoningEngine(MockLLMProvider(), PromptBuilder(), ResponseValidator())
    response = await engine.reason(ReasoningRequest(reasoning_type="incident_summary", context=context))
    assert response.snapshot_id == "snap-1"
    assert response.confidence == 80
    assert response.claims[0].source_ids == ["ev-1"]


def test_validator_rejects_unsupported_claim(snapshot_payload):
    context = SnapshotContextLoader().load(snapshot_payload)
    response = AIResponse(reasoning_type="x", snapshot_id="snap-1", snapshot_version=1,
                          answer="bad", claims=[Claim(text="unsupported", source_ids=["ev-does-not-exist"])],
                          confidence=80, priority="HIGH", model="test")
    with pytest.raises(ResponseValidationError):
        ResponseValidator().assert_valid(response, context)


def test_recommendations_are_snapshot_derived(snapshot_payload):
    context = SnapshotContextLoader().load(snapshot_payload)
    result = RecommendationGenerator().generate(context)
    assert result["immediate_actions"][0]["recommendation_id"] == "rec-1"
    assert result["blocked_by_missing_evidence"][0]["evidence_type"] == "device"
