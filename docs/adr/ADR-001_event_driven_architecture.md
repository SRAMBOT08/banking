# ADR-001: Event Driven Architecture

Context
- The platform requires decoupled services that can scale independently and support event replay.

Decision
- Use event-driven microservices as the core architecture. Services communicate primarily via Kafka.

Alternatives Considered
- Synchronous REST-only integration: rejected due to coupling and scalability limits.

Consequences
- Requires rigorous contract definitions and schema evolution strategies.
