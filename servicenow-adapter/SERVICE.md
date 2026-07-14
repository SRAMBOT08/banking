# Service Contract: ServiceNow Execution Adapter

## Responsibility

Translate approved `ExecutionTask` inputs into ServiceNow REST API operations, verify execution outcomes, emit lifecycle events, and persist immutable audit entries.

## Explicit non-responsibilities

- Policy evaluation
- Execution planning
- Investigation interpretation
- AI/LLM reasoning
- Multi-connector abstraction

## Authentication

- Basic authentication (MVP)
- OAuth2-ready design boundary through auth provider abstraction

## Retry policy

- Exponential backoff
- Retryable status code set
- Max retry cap
- Circuit-breaker-ready state model

## Verification

Incident creation verifies by re-fetching the created record and validating:

- record existence
- `sys_id` identity
- `u_investigation_id`
- `u_correlation_id`
- execution status validity

## Audit

Append-only JSONL records with hash chain integrity, including execution IDs, endpoint/method, latency, retry count, success/failure, and verification status.
