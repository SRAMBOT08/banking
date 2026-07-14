# 06 — Domain Dictionary

Canonical vocabulary for SentinelIQ. Use these terms in code, docs, and contracts.

- Evidence
  - Meaning: An atomic observed or derived fact representing telemetry or enriched data.
  - Synonyms: Observation, Fact
  - Not To Be Confused With: Alert (which is a notification triggered by rules)
  - Used By: Evidence Service, Investigation Service, AI Service

- Indicator (Threat Indicator)
  - Meaning: An IOC such as IP, domain, hash that signals malicious activity.
  - Synonyms: IOC
  - Not To Be Confused With: Evidence (indicator may be derived from evidence)
  - Used By: Knowledge Service, Evidence Service

- Threat
  - Meaning: A potential malicious actor or campaign consisting of multiple indicators and tactics.
  - Used By: Knowledge Service, Investigation Service

- Asset
  - Meaning: Any resource of value: account, server, application, device.
  - Used By: Evidence, Investigation

- Investigation
  - Meaning: A coordinated analysis process; includes hypotheses, evidence, and outcomes.
  - Used By: Investigation Service, Frontend, AI Service

- Incident
  - Meaning: A confirmed security event requiring response. Incidents may be created from Investigations.
  - Used By: Execution Service, Investigation Service

- Alert
  - Meaning: System-generated notification indicating an unusual or suspicious event.
  - Used By: Evidence Service, Investigation Service

- Transaction
  - Meaning: Financial action moving funds between accounts.
  - Used By: Ingestion, Evidence, Investigation

- Session
  - Meaning: User session metadata (login, session id, device), used for behavioral context.
  - Used By: Evidence, Investigation

- Policy
  - Meaning: Rules and thresholds for detection and actions.
  - Used By: Investigation, Evidence

- Risk
  - Meaning: Computed score representing probability/impact of compromise.
  - Used By: Frontend, Execution

- Attack Pattern
  - Meaning: Canonical attacker behavior mapped to MITRE ATT&CK.
  - Used By: Knowledge, Investigation

- Recommendation
  - Meaning: Suggested remedial action or next step produced by Investigation or AI.
  - Used By: Execution, Frontend

- Confidence
  - Meaning: Deterministic score assigned by Investigation Service; AI may provide explanatory confidence but not authoritative score.

Provenance
- Meaning: Metadata describing origin of a piece of data (source_id, evidence_id, ingestion_time, enrichment history).
- Synonyms: Lineage
- Not To Be Confused With: Confidence
- Used By: All services for auditing and governance

Canonical IDs
- Meaning: Stable identifiers assigned to canonical entities used across the platform.
- Not To Be Confused With: source-specific IDs

Temporal Fields
- first_seen, last_seen, valid_from, valid_to, event_time, ingestion_time — used across entities and required for time-based analysis and auditing.
