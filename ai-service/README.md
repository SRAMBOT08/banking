# AI Investigation Service

Phase 7 introduces SentinelIQ's replaceable AI reasoning layer. It consumes only immutable Investigation Snapshot documents and never reads raw events, normalized events, evidence graphs, threat intelligence, investigation memory, managers, or repositories.

## Architecture

`Snapshot metadata event -> Snapshot Client -> immutable AIContext -> deterministic PromptBuilder -> BaseLLMProvider -> ResponseValidator -> reports/conversation memory`

The default provider is `mock` so tests and local development require no internet. Set `LLM_PROVIDER=gemini` and provide `GEMINI_API_KEY` only for Gemini transport. The Gemini implementation defaults to `gemini-2.5-flash`; vendor details remain behind `BaseLLMProvider`.

## REST API

- `GET /health`
- `GET /models`
- `POST /reason`
- `POST /summarize`
- `POST /report`
- `POST /chat`
- `GET /history?investigation_id=...`
- `GET /metrics`

Requests may provide a complete immutable snapshot directly for tests, or `investigation_id` plus `snapshot_version`; the latter is retrieved from the Investigation Service snapshot API.

## Safety contract

Every response carries snapshot ID/version, preserves recorded confidence and priority, cites evidence or hypothesis IDs, and is rejected when citations or recommendations are not present in the snapshot. Recommendations are selected from snapshot recommendations; no new business decision is invented by this service.

## Runtime

The Docker Compose service listens on port `8600`. Kafka input is `investigation.snapshot.created.v1`; outputs are `investigation.reasoned.v1`, `investigation.report.generated.v1`, and `investigation.ai.metrics.v1`. Conversation memory and caches are process-local by design.
