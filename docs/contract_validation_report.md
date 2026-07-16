# Contract Validation Report

| Boundary | Harness contract | Result |
|---|---|---|
| Simulator → Ingestion | event ID, correlation ID, tenant ID, event timestamp, ingestion timestamp | PASS |
| Ingestion → Evidence | normalized, deduplicated event records | PASS |
| Evidence → Threat | evidence IDs and deterministic matched pattern | PASS |
| Threat → Knowledge | scenario pattern and matched evidence | PASS |
| Knowledge → Graph | enrichment and entity relationship records | PASS |
| Graph → Memory | graph context and historical lookup shape | PASS |
| Intelligence → Aggregator | evidence, threat, knowledge, graph, historical context, timeline, provenance | PASS |
| Aggregator → Agent | completed context metadata and provenance | PASS |
| Agent → Case Builder | hypotheses, confidence sources, decision, recommendations | PASS |
| Case Builder → AI Report | case ID, version, metadata, sections, audit, provenance | PASS |
| Case Builder → Execution | case ID, tenant, correlation, version, recommendations | PASS |
| Execution → ServiceNow | execution ID, operation, action payload, case ID | PASS (mock adapter) |

## Live topology findings

- Evidence does not currently publish `evidence.graph.events.v1`.
- Attack knowledge emits `pattern`, while investigation expects `pattern_name`.
- Compose runs `knowledge-service` as `busybox`.
- Investigation has no confirmed `investigation.completed.v1` producer.
- Case Builder and AI Report Service have no automatic caller.
- ServiceNow requires credentials or a transport-backed mock.

These are integration deployment gaps, not hidden behind the in-process harness.
