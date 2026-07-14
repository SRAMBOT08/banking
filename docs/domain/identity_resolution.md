# Identity Resolution Strategy

Purpose
- Define how the platform establishes canonical entity IDs, maps source identifiers, and resolves conflicts.

Components

- Canonical Entity IDs
  - Each principal entity (Customer, Account, Device, IP) must have a stable canonical ID assigned in shared models. Canonical IDs are immutable references used across services.

- Source Mapping
  - Store original source identifiers alongside canonical IDs with `source_id` and `source_entity_id`. This mapping is owned by the Ingestion Service and persisted for lineage.

- Merge Rules
  - Merge rules are policy-driven and documented here: when two records map to the same canonical ID, the platform records a merge event and preserves provenance for both records. Merge events are emitted to `events.unified.v1` with type `identity.merge.v1`.

- Conflict Resolution
  - Conflicts (contradictory authoritative attributes) are surfaced to Investigation Service as a `identity.conflict.v1` event for human review. Automatic reconciliation requires explicit policy and is out of scope for Phase 2.

- Idempotency and Determinism
  - Identity resolution must be deterministic given the same inputs. Any non-deterministic resolution must be logged and require human review.

Ownership
- Ingestion Service owns source mappings and initial canonicalization.
- Investigation Service owns merge/conflict resolution workflows (human-in-the-loop).

Notes
- Implementation details (algorithms and thresholds) will be defined in Phase 3 and codified in shared models and contract tests.
