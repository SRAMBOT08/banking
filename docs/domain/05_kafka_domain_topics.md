# 05 — Kafka Domain Topics

Topic design for Phase 1. Naming convention: <domain>.<entity>.<action>.v<major>

Topics

- events.unified.v1
  - Purpose: Canonicalized telemetry/transaction events from ingestion
  - Producer: ingestion-service
  - Consumer: evidence-service, investigation-service
  - Schema Name: UnifiedEvent.v1
  - Retention: default broker retention (configurable)
  - Dead Letter Queue: events.unified.dlq.v1
  - Retry Strategy: consumer-side exponential backoff with DLQ after N retries
  - Versioning Strategy: major version increment for breaking changes

- evidence.graph.events.v1
  - Purpose: Graph update events emitted by Evidence Service
  - Producer: evidence-service
  - Consumer: investigation-service, ai-service
  - Schema Name: EvidenceGraphEvent.v1
  - DLQ: evidence.graph.events.dlq.v1

- knowledge.graph.updated.v1
  - Purpose: Knowledge graph updates (imports/edits)
  - Producer: knowledge-service
  - Consumer: investigation-service, evidence-service
  - Schema Name: KnowledgeGraphUpdate.v1

- investigations.updated.v1
  - Purpose: Investigation lifecycle events
  - Producer: investigation-service
  - Consumer: ai-service, execution-service, frontend (via gateway)
  - Schema Name: InvestigationEvent.v1

- ai.responses.v1
  - Purpose: AI-generated explanations and summaries
  - Producer: ai-service
  - Consumer: frontend, investigation-service
  - Schema Name: AIResponse.v1

- execution.requests.v1
  - Purpose: Requests to perform external actions (tickets, notifications)
  - Producer: investigation-service (sole producer). Frontend MUST NOT publish directly to Kafka; operator actions must go through Gateway → Investigation Service.
  - Consumer: execution-service
  - Schema Name: ExecutionRequest.v1

- execution.status.v1
  - Purpose: Status updates for execution requests
  - Producer: execution-service
  - Consumer: investigation-service, frontend
  - Schema Name: ExecutionStatus.v1

Topic Governance
- Each topic must have a single producing service owner; enforcement is required (see `docs/adr/ADR-002_apache_kafka.md`).
- Frontend is explicitly forbidden from publishing directly to Kafka; all UI-originated requests are routed through the Gateway to the owning service.
- Schemas must be versioned and stored in `docs/contracts/` and `shared/schemas/`.
- Consumers must implement idempotency and deduplication guidance from `docs/contracts/unified_event_model.md`.

New topic: audit.events.v1
  - Purpose: Centralized audit and access log events for governance, compliance and lineage
  - Producer: gateway (audits), investigation-service (investigation audits), execution-service (action audits). Multiple producers allowed but writes must be append-only and idempotent; audit consumers are read-only.
  - Consumer: governance tooling, archiver
  - Schema Name: AuditEvent.v1
  - DLQ: audit.events.dlq.v1

DLQ and Retry Strategy (global)
- Default consumer retry policy: 3 attempts with exponential backoff (e.g., base 1s, factor 2) before writing to the topic-specific DLQ.
- DLQ ownership: the owner of the producing topic is responsible for monitoring and reprocessing DLQ messages. For example, DLQs for `events.unified.v1` are the responsibility of ingestion-service; for `evidence.graph.events.v1` evidence-service owns the DLQ.
- Reprocessing policy: messages in DLQ must be inspected, fixed (if schema issue) and reprocessed via controlled reingestion processes. Retention for DLQ: default 7 days (configurable per org) unless otherwise specified by Data Governance.

Enforced single-producer decisions
- `execution.requests.v1` producer: Investigation Service is the sole producer. Frontend operator actions must be sent to Gateway → Investigation Service.
- All other topics in this document are assigned a single producing service in their definitions; if multi-producer topics are required (like `audit.events.v1`) they must be explicitly approved by ADR and have strict append-only semantics.
