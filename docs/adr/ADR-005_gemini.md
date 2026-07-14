# ADR-005: Gemini Integration

Context
- AI capabilities required for explanations and summaries.

Decision
- Isolate all LLM interactions in `ai-service`. LLMs will be called only for explanation, summary and non-decisional outputs.

Consequences
- `ai-service` must be auditable and implement strict request/response logging in Phase 2.
