# 04 — Service Communication Matrix

Matrix describing what each service consumes/produces, external APIs, databases and Kafka topics (Phase 1 — high level).

Gateway
- Consumes: HTTP/WebSocket requests from Frontend
- Produces: gateway.audit.v1
- External APIs: Identity Provider (OIDC) — integration placeholder
- Database: none
- Dependencies: shared

Ingestion Service
- Consumes: external telemetry feeds
- Produces: events.unified.v1
- External APIs: various telemetry adapters
- Database: none (stateless)
- Dependencies: shared

Evidence Service
- Consumes: events.unified.v1
- Produces: evidence.graph.events.v1
- External APIs: Neo4j (writes)
- Database: Neo4j (evidence graph)
- Dependencies: shared

Knowledge Service
- Consumes: admin imports
- Produces: knowledge.graph.updated.v1
- External APIs: MITRE/Threat Feeds
- Database: Neo4j (knowledge graph)
- Dependencies: shared

Investigation Service
- Consumes: evidence.graph.events.v1, knowledge.graph.updated.v1
- Produces: investigations.updated.v1
- External APIs: none in Phase 1
- Database: PostgreSQL (investigations, policies, audit)
- Dependencies: shared

AI Service
- Consumes: investigation.context.requests.v1
- Produces: ai.responses.v1
- External APIs: LLM providers (Gemini) — credentials external
- Database: none (stateless)
- Dependencies: shared

Execution Service
- Consumes: execution.requests.v1
- Produces: execution.status.v1
- External APIs: ServiceNow/Jira/Teams (provider placeholders)
- Database: none in Phase 1
- Dependencies: shared

Notes
- Each Kafka topic has one producing service owner (documented in `05_kafka_domain_topics.md`).
- All service-to-service durable communication must flow through Kafka topics; direct DB access is forbidden.
