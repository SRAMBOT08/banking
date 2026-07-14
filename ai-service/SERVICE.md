# AI Investigation Service Contract

## Input boundary

The sole domain input is an immutable `InvestigationSnapshot`. Kafka carries snapshot metadata; the service retrieves the corresponding snapshot through the Investigation Service snapshot endpoint. No other platform data source is permitted.

## Components

- Provider strategy: `BaseLLMProvider`, `GeminiProvider`, `MockLLMProvider`, and factory.
- `SnapshotContextLoader`: creates frozen `AIContext` with only investigation, timeline, evidence, hypotheses, recommendations, priority, confidence, confidence history, graph summary, related investigations, missing evidence, and metadata.
- `PromptBuilder`: deterministic specialized templates.
- `ReasoningEngine`: structured reasoning requests and provider responses.
- `ResponseValidator`: rejects unsupported citations, changed confidence/priority, unknown hypotheses, and invented recommendations.
- `RecommendationGenerator`: snapshot-derived action groups.
- `ReportGenerator`: executive, SOC, technical, compliance, and fraud report structure in JSON or Markdown-compatible data.
- `ConversationMemory`: AI-only process-local history with prompt, response, model, usage, latency, reasoning type, and snapshot version.

## Kafka

Consumes `investigation.snapshot.created.v1` and publishes `investigation.reasoned.v1`, `investigation.report.generated.v1`, and `investigation.ai.metrics.v1`.

## Configuration

`LLM_PROVIDER=mock` is the safe default. Gemini settings include `GEMINI_API_KEY`, `GEMINI_MODEL`, temperature, top-p, top-k, max tokens, timeout, retry count, backoff, and streaming flag. No API key is hardcoded.
