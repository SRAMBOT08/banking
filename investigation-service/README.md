# Investigation Service

Deterministic, memory-only orchestration between Threat Intelligence candidates and the future AI Investigation Service.

## Responsibilities

- Consume `investigation.candidates.v1`
- Correlate candidates by correlation ID and shared entities
- Deduplicate hypotheses and evidence
- Maintain investigation lifecycle and state transitions
- Build chronological timelines
- Aggregate evidence and confidence
- Identify missing evidence
- Assign deterministic priority
- Publish `investigation.active.v1`

The service performs no AI reasoning, external integrations, final security decisions, persistence, or playbook execution.

## Phase 6.5 components

- `InvestigationMemory`: append-only process-local event history.
- `InvestigationContextBuilder`: creates the single typed context package consumed by the future AI service.
- `InvestigationPolicy`: owns transition, escalation, lifetime, and auto-close policies.
- `InvestigationReplay`: reconstructs chronological state and confidence history from memory events.
- `InvestigationMetricsEngine`: computes deterministic in-memory operational metrics.
- `build_investigation_graph`: produces investigation-only graph visualization and traversal data; it is not the Evidence Graph.
- `SnapshotManager`: creates and retrieves immutable, versioned investigation snapshots.
- `SnapshotValidator`, `SnapshotDiffEngine`, `SnapshotSerializer`, and `SnapshotMetrics`: validate, compare, serialize, and measure snapshots deterministically.

## REST API

The service exposes `/health`, `/metrics`, and `/investigations` endpoints, with equivalent `/api/v1` routes. Investigation resources provide timeline, memory, graph, context, replay, recommendations, missing-evidence, transition, close, and reopen operations. Snapshot resources provide list, latest, version lookup, immutable context, diff, and manual creation operations. Responses are typed Pydantic models.

## Event contract

Input remains `investigation.candidates.v1`. Typed versioned `InvestigationEvent` envelopes are published to `investigation.active.v1` and `investigation.updated.v1`; lifecycle-specific events use `investigation.closed.v1` and `investigation.escalated.v1`. Event IDs are deterministic hashes of event type, investigation ID, timestamp, and update timestamp. No existing upstream contract is changed.

Every mutation creates an append-only memory event and structured log entry. Memory is intentionally process-local and is cleared on restart.

## Phase 6.6 snapshots

Snapshots are complete detached copies of investigation state. They include the investigation, timeline, evidence, hypotheses, confidence, confidence history, recommendations, missing evidence, graph, related investigations, metadata, memory, and summary. Snapshot versions start at `1`, increment monotonically per investigation, and reference their parent snapshot. Stored snapshots are returned as defensive copies and deletion is disabled unless explicitly allowed by policy.

Snapshot metadata is published to `investigation.snapshot.created.v1`; the event contains no full snapshot payload. Future AI consumers must retrieve the immutable snapshot through this service rather than reading live investigation state.

## Run

The Docker Compose service listens on port `8500`. The API exposes health, list, retrieval, and validated state-transition endpoints. All runtime state is lost on restart by design.
