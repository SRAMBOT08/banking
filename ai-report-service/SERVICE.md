# SentinelIQ AI Report Service

The AI Report Service is a downstream, CaseFile-only report renderer. It does not investigate incidents, call intelligence services, calculate confidence, classify attacks, generate hypotheses, or modify CaseFile data.

## Flow

`CaseFile -> ContextBuilder -> PromptBuilder -> Guardrails -> ModelProvider -> ReportValidator -> Formatter -> Repository`

`CaseFile` is accepted as its serialized immutable wire shape. The service intentionally does not import `case-service` so the deployment boundary remains replaceable.

## API

- `GET /health`
- `POST /api/v1/reports`
- `GET /api/v1/reports/{report_id}`
- `GET /api/v1/reports/case/{case_id}/history`
- `GET /api/v1/reports/search`
- `GET /api/v1/reports/statistics`

Supported report types are executive, technical, SOC, root-cause, timeline, MITRE, fraud, business-impact, recommendations, and compliance. Formats are Markdown, HTML, JSON, and PDF-ready.

## Providers

`ModelProvider` is the stable abstraction. `NIMProvider` speaks the NVIDIA NIM-compatible chat-completions API. `DeterministicNIMProvider` is the default for local tests and does not invent facts. Future providers can be added without changing report orchestration.

## Immutability and validation

Reports are append-only and repository reads are deep-copied. Prompt guardrails reject empty, oversized, or injection-marked prompts. Response validation requires mandatory sections and exact CaseFile traceability.
