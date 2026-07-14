# 01 — Domain Model

This document enumerates the business entities for SentinelIQ. Each entity includes Purpose, Description, Owner, Lifecycle, Attributes, Relationships, and Used By.

Entities

- User
  - Purpose: Human operator or system account interacting with the platform.
  - Description: Represents a person or service identity with roles and permissions.
  - Owner: Gateway / Identity management (external) — platform-level ownership in registry.
  - Lifecycle: Created → Activated → Suspended → Deactivated → Deleted (audit retained)
  - Attributes: id, username, display_name, roles, email, last_login, status, created_at, updated_at
  - Relationships: OWNS Investigations; ASSIGNED_TO Tickets
  - Used By: Gateway, Frontend, Execution Service, Investigation Service

- Customer
  - Purpose: The bank's retail or corporate customer.
  - Description: Account holder with KYC and profile data.
  - Owner: PostgreSQL (investigation-service domain ownership)
  - Lifecycle: Onboarded → Verified → Active → Closed
  - Attributes: customer_id, name, kyc_status, contact_info, created_at
  - Relationships: OWNS Accounts; RELATED_TO Transactions
  - Used By: Ingestion, Evidence, Investigation, Execution

- Account
  - Purpose: Financial account owned by a Customer.
  - Description: Represents bank account metadata used to link transactions.
  - Owner: PostgreSQL (investigation-service)
  - Lifecycle: Opened → Active → Suspended → Closed
  - Attributes: account_id, account_type, currency, status, owner_customer_id
  - Relationships: CONTAINS Transactions; HAS Beneficiaries
  - Used By: Ingestion, Evidence, Investigation

- Transaction
  - Purpose: Represents a monetary transfer or operation.
  - Description: Source of potential fraud signals and correlation input.
  - Owner: Ingestion / Event stream canonicalization (ingestion-service creates canonical events)
  - Lifecycle: Created → Posted → Settled → Reconciled
  - Attributes: transaction_id, amount, currency, timestamp, from_account, to_account, status, metadata
  - Relationships: SENT_TO Beneficiary; INITIATED_BY User/Device
  - Used By: Evidence, Investigation, Execution

- Beneficiary
  - Purpose: Counterparty/recipient for transactions.
  - Description: External or internal recipient tied to accounts.
  - Owner: PostgreSQL (investigation-service)
  - Attributes: beneficiary_id, name, account_reference, relationship_type
  - Relationships: RECEIVES Transaction
  - Used By: Investigation, Execution

- Device
  - Purpose: Endpoint used by users/customers to interact with banking services.
  - Description: Device fingerprint and telemetry for behavioral correlation.
  - Owner: Ingestion/Evidence (device identity canonicalization in evidence-service)
  - Attributes: device_id, device_type, os, fingerprint, last_seen
  - Relationships: USED_BY User; ASSOCIATED_WITH Session/IP
  - Used By: Evidence, Investigation

- IP
  - Purpose: Network address entity for telemetry correlation.
  - Description: IP address with enrichment metadata (ASN, geo).
  - Owner: Evidence Service (graph node)
  - Attributes: ip_address, asn, geo, reputation_score
  - Relationships: USED_BY Device/Session; MATCHES Threat Indicator
  - Used By: Evidence, Investigation

- Threat Indicator
  - Purpose: Indicator of compromise (IOC).
  - Description: Hashes, domains, URLs, IPs, signatures mapped to threat intelligence.
  - Owner: Knowledge Service
  - Attributes: indicator_id, type, value, source, confidence, last_seen
  - Relationships: MATCHES IP/Device/File/URL; MAPPED_TO Attack Pattern
  - Used By: Evidence, Investigation, Knowledge

- Alert
  - Purpose: System-generated notification indicating potential malicious activity.
  - Description: Derived from correlation rules or policy triggers.
  - Owner: Investigation Service / Evidence Service (depending on origin)
  - Attributes: alert_id, severity, rule_id, source_event_id, created_at, status
  - Relationships: TRIGGERS Investigation; CONTAINS Evidence
  - Used By: Investigation, Execution, Frontend

- Asset
  - Purpose: Logical or physical asset tracked by the platform.
  - Owner: Evidence Service / Inventory sync
  - Attributes: asset_id, type, owner, location, criticality
  - Relationships: HOSTS Device; ASSOCIATED_WITH Accounts
  - Used By: Investigation, Policy

- Evidence
  - Purpose: Atomic observed facts used in investigations and graphs.
  - Description: Normalized events, enriched data, and derived observations represented as graph nodes.
  - Owner: Evidence Service (Evidence Graph in Neo4j)
  - Lifecycle: Ingested → Enriched → Linked → Archived
  - Attributes: evidence_id, source_event_id, type, timestamp, payload_summary, confidence
  - Relationships: PART_OF Investigation; LINKS_TO Entities (Account, Transaction, Device, IP)
  - Used By: Investigation, AI, Knowledge

- Investigation
  - Purpose: Orchestration object representing a triage and analysis process.
  - Owner: Investigation Service (Postgres stored state)
  - Lifecycle: Created → In Progress → Resolved → Closed
  - Attributes: investigation_id, status, owner_user_id, priority, hypothesis_list, created_at, updated_at
  - Relationships: CONTAINS Evidence; RELATED_TO Alerts; LINKS_TO Recommendations
  - Used By: Frontend, AI, Execution

- Attack Pattern
  - Purpose: Canonical representation of attacker behaviors (mapped to MITRE ATT&CK)
  - Owner: Knowledge Service
  - Attributes: attack_id, name, description, mitre_mapping, severity, detection_tips
  - Relationships: MAPPED_TO Threat Indicators; ASSOCIATED_WITH Recommendations
  - Used By: Investigation, Evidence

- Policy
  - Purpose: Detection or response policy defining rules and thresholds.
  - Owner: Investigation Service / Policy Management (Postgres)
  - Attributes: policy_id, name, description, rule_spec, severity, enabled
  - Relationships: TRIGGERS Alerts; APPLIES_TO Assets/Accounts
  - Used By: Evidence, Investigation, Execution

- Risk
  - Purpose: Derived risk score for entities (accounts, customers, devices).
  - Owner: Investigation Service
  - Attributes: risk_id, subject_type, subject_id, score, reason, computed_at
  - Relationships: ATTACHED_TO Account/Customer/Asset
  - Used By: Frontend, Execution

- Case
  - Purpose: Business-level case management grouping investigations and actions.
  - Owner: Execution Service (ticketing integration)
  - Attributes: case_id, title, description, status, linked_investigations
  - Relationships: CONTAINS Investigations; LINKS_TO Tickets
  - Used By: Execution, Frontend

- Recommendation
  - Purpose: Suggested actions produced by Investigation or AI.
  - Owner: Investigation Service / AI Service (suggestion origin tracked)
  - Attributes: recommendation_id, type, description, rationale, confidence_estimate
  - Relationships: ATTACHED_TO Investigation; TRIGGERS Execution
  - Used By: Execution, Frontend

- Ticket
  - Purpose: External workflow artifact (ServiceNow/Jira) created to track remediation.
  - Owner: Execution Service
  - Attributes: ticket_id, provider, status, external_url, created_at
  - Relationships: REPRESENTS Case/Recommendation
  - Used By: Execution, Frontend

- Notification
  - Purpose: Messaging artifact to inform users/operators of events or actions.
  - Owner: Execution Service
  - Attributes: notification_id, channel, recipient, message, status
  - Relationships: RELATED_TO Ticket/Case/Investigation
  - Used By: Execution, Frontend

Notes
- Each entity must be represented in shared models as a contract before implementation.
- Ownership indicates which service owns the authoritative source of truth for that entity.

-- Organization (NEW)
  - Purpose: Represents the bank, tenant, or organizational boundary for data and configuration.
  - Description: Top-level tenant model which scopes Customers, Accounts, Policies, Connectors and service configurations.
  - Owner: Platform / Ops (documented ownership); scoped references used by all services
  - Lifecycle: Registered → Active → Suspended → Decommissioned
  - Attributes: org_id, name, legal_entity, region, connectors, retention_policies
  - Relationships: OWNS Customers, Accounts, Knowledge sources
  - Used By: All services for data scoping and tenancy

-- Source (NEW)
  - Purpose: Canonical record describing provenance of data (telemetry feeds, vendor feeds, core banking systems).
  - Description: Identifies upstream origin of events, enrichments and knowledge artifacts. Used for trust, lineage and reprocessing.
  - Owner: Ingestion Service (owners of source registration) and Governance (platform)
  - Lifecycle: Registered → Active → Deprecated → Removed
  - Attributes: source_id, name, source_type, owner_org_id, trust_score, last_ingest_at
  - Relationships: PRODUCES Transactions/Events; PROVIDES Knowledge feeds
  - Used By: Ingestion, Evidence, Knowledge, Investigation

-- Enrichment (NEW)
  - Purpose: Represents external enrichment applied to entities (threat intel, geo, device fingerprinting).
  - Description: Tracks enrichment source, type and confidence.
  - Owner: Evidence Service (applies) / Knowledge Service (provides)
  - Attributes: enrichment_id, source_id, type, value, confidence, timestamp
  - Relationships: ATTACHED_TO Evidence/Entity
  - Used By: Evidence, Investigation

Temporal attributes (applies to many entities)
- first_seen: timestamp when entity was first observed
- last_seen: timestamp when entity was most recently observed
- valid_from / valid_to: validity window for derived or authoritative attributes
- event_time: original event timestamp
- ingestion_time: time event was ingested into platform

Identity & Resolution
- Canonical IDs: every principal entity must have a stable canonical id (e.g., customer_id, account_id, device_id)
- Source Mapping: original source id must be stored with mapping to canonical id
- Merge Rules: documented merge rules will be created in `docs/domain/identity_resolution.md`
- Conflict Resolution: conflicts require investigation and are surfaced to Investigation Service; last-writer-wins is not the default

Evidence Provenance
- Every graph node and relationship MUST reference the originating evidence_id(s) and source_id(s). Provenance metadata includes source, ingestion_time and enrichment references.

Confidence Propagation
- Confidence must be recorded at multiple layers:
  - Node level: confidence score for entity extraction/enrichment
  - Relationship level: confidence for inferred links
  - Hypothesis level: confidence for a hypothesis within an investigation
  - Investigation level: aggregated deterministic confidence (Investigation Service authoritative)
  - AI-provided confidence/explanations are non-authoritative and must be labeled as such
