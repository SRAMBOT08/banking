# 08 — Sequence Overview

End-to-end business flow (high level):

1. External Systems (banking systems, telemetry feeds) emit events.
2. Ingestion Service consumes, validates, deduplicates and publishes `events.unified.v1`.
3. Evidence Service consumes `events.unified.v1`, performs entity extraction and writes Evidence Graph (Neo4j); emits `evidence.graph.events.v1`.
4. Knowledge Service maintains and updates Attack Knowledge Graph; emits `knowledge.graph.updated.v1` on changes.
5. Investigation Service consumes evidence and knowledge updates, runs deterministic correlation and scoring, creates/updates investigations and emits `investigations.updated.v1`.
6. AI Service consumes investigation context requests and returns explainability payloads via `ai.responses.v1`.
7. Investigation Service (operator or policy) issues `execution.requests.v1` to Execution Service.
8. Execution Service performs provider actions (tickets/notifications) and emits `execution.status.v1`.
9. Frontend and operators review via Gateway APIs and WebSockets.

Notes: each stage persists only what it owns; communication is via Kafka topics and stable IDs.
