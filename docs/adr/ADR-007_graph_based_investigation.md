# ADR-007: Graph-based Investigation

Context
- Investigation workloads benefit from graph traversal and pattern matching.

Decision
- Use graph representations for evidence and attack knowledge; keep graph modeling in `evidence-service` and `knowledge-service` ownership boundaries.

Consequences
- Graph design must be standardized across services via contracts.
