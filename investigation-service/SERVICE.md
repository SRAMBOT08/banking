Investigation Service Contract

Responsibility:
- Hypothesis engine, graph matching, confidence scoring (deterministic), policy engine, orchestration.

Inputs:
- evidence.graph.events.v1
- knowledge.graph.updated.v1

Outputs:
- investigations.updated.v1

Kafka Topics Produced:
- investigations.updated.v1

Kafka Topics Consumed:
- evidence.graph.events.v1
- knowledge.graph.updated.v1

Database Ownership:
- Investigations, Audit Logs, Policies (PostgreSQL)

External Integrations:
- None in Phase 1

Dependencies:
- shared library

Shared Models Used:
- shared.models.investigation.*
