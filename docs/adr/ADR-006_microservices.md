# ADR-006: Microservices

Context
- Services must be independently deployable and own bounded contexts.

Decision
- Adopt microservices per the project specification. Each service will own its data and expose contracts via Kafka and APIs where required.

Consequences
- Requires strict contracts and cross-team coordination.
