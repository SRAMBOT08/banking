# Unified Event Model

This document defines the canonical event envelope used across SentinelIQ microservices.

(Architecture contract only — no implementation.)

Sections:
- Envelope fields (id, type, timestamp, source, schema_version, payload)
- Idempotency and deduplication keys
- Correlation identifiers
- Schema versioning rules
- Example JSON Schema (appendix)
