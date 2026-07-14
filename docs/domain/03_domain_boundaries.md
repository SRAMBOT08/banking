# 03 — Domain Boundaries

This document defines service ownership and clear boundaries for each domain area. No overlapping ownership; references only.

Service Ownership

- Gateway
  - Owns: API routing, authentication gateway, request-level audit events (non-authoritative)
  - Does not own business data

- Ingestion Service
  - Owns: Canonicalization of external telemetry into Unified Event Model; topic publishing for normalized events
  - Responsible for: schema validation, deduplication keys

- Evidence Service
  - Owns: Evidence Graph (Neo4j) — authoritative representation of observed entities and linkages
  - Responsible for: entity extraction, resolution, enrichment, and evidence lifecycle

- Knowledge Service
  - Owns: Attack Knowledge Graph (Neo4j) and threat ontology; authoritative threat indicators and mappings to MITRE
  - Responsible for: knowledge ingestion and versioning

- Investigation Service
  - Owns: Investigation state, deterministic confidence calculations, policies, and PostgreSQL data (investigations/audit)
  - Responsible for: orchestration and business decisioning (excluding AI suggestions)

- AI Service
  - Owns: LLM orchestration and explainability outputs (stateless)
  - Responsible for: generating summaries, explanations, and counterfactual reasoning only; must not make decisions or compute confidence

- Execution Service
  - Owns: Provider integration for ticketing, notifications, and external workflows; provider pattern implementations
  - Responsible for: ensuring idempotent external side-effects

Ownership rules
- A graph object (node or relationship) belongs to exactly one service: Evidence Graph nodes — Evidence Service; Attack Knowledge nodes — Knowledge Service.
- Cross-service references use stable IDs and events; services MUST NEVER query another service's database directly. This is a hard constraint: all cross-service communication must be via events (Kafka) or stable service APIs. Direct DB access is forbidden and will be treated as a violation of architecture.
- Schema changes to shared models require ADR and versioning in `shared/` before deployment.

Neo4j decision (MVP)
- For the MVP we will use a single Neo4j instance. Evidence Service owns the Evidence Graph namespace and Knowledge Service owns the Knowledge Graph namespace (separate named databases if supported). Cross-graph links are implemented via stable IDs and event-driven updates; no service writes into another service's graph namespace.
