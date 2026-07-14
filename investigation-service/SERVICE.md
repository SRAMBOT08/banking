# Investigation Service Contract

## Input

- Topic: `investigation.candidates.v1`
- Consumer group: `investigation-service-group`
- Candidate validation occurs before orchestration.

## Output

- Topic: `investigation.active.v1`
- Payload: typed `Investigation` model containing state, priority, confidence, timeline, evidence summary, hypotheses, related entities, missing evidence, investigation plan, next action, explanation, and metadata.

## Deterministic pipeline

Candidate consumer → validator → correlator → deduplication → investigation manager → timeline → evidence aggregation → confidence → missing evidence → priority → state machine → explainability → publisher.

## State machine

`NEW → OPEN → COLLECTING_EVIDENCE → CORRELATING → ANALYZING → WAITING_FOR_EVIDENCE → READY_FOR_AI → ESCALATED → RESOLVED → CLOSED`.

Only explicitly declared transitions are accepted. Reopening is supported from `CLOSED` to `OPEN`.

## Storage and integrations

The repository is process-local memory only. No PostgreSQL, Redis, Neo4j, AI, Gemini, external API, decision engine, human approval, or execution integration is implemented.

## Phase 6.5 guarantees

All context, replay, graph, metrics, and event outputs are deterministic for the same ordered input sequence. Memory events have monotonic per-investigation sequence numbers and deterministic IDs. Policy checks are isolated from `InvestigationManager`; the manager orchestrates policy, domain engines, repository, and memory.

The investigation context is the only aggregation boundary required by the future AI Investigation Service. It contains the investigation snapshot, timeline, evidence, hypotheses, pattern matches, confidence and history, missing evidence, recommendations, graph data, related entities, related investigations, memory, and metadata.

## Phase 6.6 snapshot contract

The Snapshot Engine is the official immutable context source. `SnapshotManager` coordinates `SnapshotBuilder`, `SnapshotRepository`, `SnapshotVersionManager`, `SnapshotValidator`, `SnapshotSerializer`, `SnapshotDiffEngine`, and `SnapshotMetrics`. Snapshots are process-local, never persisted to a database or filesystem, and are defensively copied on write and read.

Snapshot metadata contains `snapshot_id`, monotonically increasing `snapshot_version`, `investigation_version`, `created_at`, `created_by`, `reason`, and `parent_snapshot`. The metadata-only Kafka event is published on `investigation.snapshot.created.v1`; the full snapshot remains available only through the Investigation Service REST API.

Snapshot APIs:

- `GET /investigations/{id}/snapshots`
- `GET /investigations/{id}/snapshots/latest`
- `GET /investigations/{id}/snapshots/{version}`
- `GET /investigations/{id}/snapshots/{version}/context`
- `GET /investigations/{id}/snapshots/diff?from_version=x&to_version=y`
- `POST /investigations/{id}/snapshots`
