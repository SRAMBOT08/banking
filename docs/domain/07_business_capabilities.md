# 07 — Business Capabilities

Capabilities map to services and are the building blocks for product features.

- Event Ingestion
  - Inputs: Raw telemetry, transaction streams
  - Outputs: events.unified.v1
  - Owner: Ingestion Service
  - Dependencies: shared, Kafka

- Evidence Intelligence
  - Inputs: events.unified.v1
  - Outputs: evidence.graph.events.v1
  - Owner: Evidence Service
  - Dependencies: shared, Neo4j

- Graph Construction
  - Inputs: normalized events, enrichments
  - Outputs: graph nodes/relationships (evidence graph)
  - Owner: Evidence Service
  - Dependencies: Neo4j, shared

- Threat Correlation
  - Inputs: Evidence, Knowledge
  - Outputs: Alerts, linked Evidence
  - Owner: Evidence Service / Investigation Service (co-owned by contract)
  - Dependencies: Knowledge Service

- Attack Pattern Matching
  - Inputs: Evidence Graph, Knowledge Graph
  - Outputs: Matches to Attack Patterns
  - Owner: Investigation Service
  - Dependencies: Evidence Service, Knowledge Service

- Investigation
  - Inputs: Alerts, Evidence, Knowledge matches
  - Outputs: investigations.updated.v1, Recommendations
  - Owner: Investigation Service
  - Dependencies: shared, PostgreSQL

- AI Explanation
  - Inputs: investigation context
  - Outputs: ai.responses.v1
  - Owner: AI Service
  - Dependencies: shared, LLM provider

- Decision Intelligence
  - Inputs: Investigation results, Policies
  - Outputs: Execution requests, Risk updates
  - Owner: Investigation Service
  - Dependencies: Execution Service

- Execution
  - Inputs: execution.requests.v1
  - Outputs: execution.status.v1, Tickets, Notifications
  - Owner: Execution Service
  - Dependencies: external ticketing providers, shared

- Monitoring & Audit
  - Inputs: service logs, audits, events
  - Outputs: audit records, alerts
  - Owner: Cross-cutting (shared instrumentation)
  - Dependencies: shared
