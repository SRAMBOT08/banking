# Architectural Decisions

- Event Driven via Kafka: decouples producers/consumers and supports high throughput and replay.
- Microservices with DDD: each service owns a bounded context and its data.
- Clean Architecture & SOLID: services separated into layers to enable testability and evolution.
- Neo4j for graph stores and PostgreSQL for relational data.
- AI interactions isolated in `ai-service` to enforce separation of concerns and auditability.
- All configuration via environment variables to support 12-factor app.
- Docker Compose for local development; Kubernetes is expected in Phase 2.
