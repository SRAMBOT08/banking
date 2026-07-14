# Confidence Propagation

Purpose
- Define how confidence scores are captured, propagated and aggregated across the platform.

Levels

- Node Level
  - Each graph node (Evidence, Entity) may carry a `confidence` score (0.0 - 1.0) representing extraction/enrichment confidence.

- Relationship Level
  - Relationships derived or inferred must carry a `confidence` score describing the strength of the linkage.

- Hypothesis Level
  - Hypotheses generated during investigation contain confidence estimates derived from contributing node/relationship confidences and deterministic scoring rules.

- Investigation Level
  - Investigation Service computes an aggregated deterministic confidence for the investigation; this score is authoritative for decisioning.

Rules
- Confidence scores must include provenance: source component, contributing evidence_ids, timestamp, and computation version.
- AI-provided confidence is advisory only and tagged as non-authoritative.
- Confidence aggregation algorithm is defined in Phase 3 and must be deterministic and auditable.
