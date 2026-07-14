# 11 — Data Governance

Purpose
- Define PII handling, retention, lineage, schema ownership, DLQ policies, and auditing for SentinelIQ.

Scope
- Applies to all data stores, Kafka topics, schema definitions, and Neo4j graph data.

Key Policies

- PII and Sensitive Data
  - All PII must be classified and handled per bank policies. Sensitive fields must be masked in logs and audit streams. Shared models must annotate PII fields.

- Retention
  - Default retention for event topics: as configured per org; DLQs default 7 days. Datastore retention and archival policies must be defined per Organization.

- Lineage and Provenance
  - All derived entities and graph objects must reference origin `source_id`, `evidence_id`, `ingestion_time`, and enrichment history.

- Schema Ownership
  - Each schema has a single owner (service) and is versioned. Changes follow ADR approval and consumer-driven contract testing.

- DLQ & Retry
  - Each topic DLQ is owned by the producing service. DLQ messages are reprocessed by the producing team after inspection.

- Audit
  - Audit events are published to `audit.events.v1`. Gateway, Investigation Service and Execution Service are producers of audit records. Audit consumers (archiver/compliance) are read-only and external.

Governance Processes
- Schema changes require an ADR and a changelog entry. Breaking changes require major version bump and consumer migration plan.
- PII field additions must be approved by Data Governance and annotated in shared models.

Contacts
- Platform / Data Governance Team (placeholder)
