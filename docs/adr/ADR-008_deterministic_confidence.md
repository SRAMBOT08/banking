# ADR-008: Deterministic Confidence

Context
- Confidence calculations must be auditable and deterministic.

Decision
- Confidence scoring algorithms are part of Investigation Service domain and must be deterministic and reproducible; AI service may provide explanations but not compute confidence.

Consequences
- Define audit trails and versioned scoring models in Phase 2.
