# ADR-002: Apache Kafka

Context
- Need a durable, scalable event backbone.

Decision
- Use Apache Kafka for asynchronous messaging. Schema registry and serialization strategy deferred to Phase 2.

Consequences
- Operational complexity; must define topics, retention, and schema management.
