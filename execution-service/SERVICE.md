# Execution Decision & Orchestration Service Contract

## Responsibility

Deterministically transform completed investigations into governed execution plans, task lifecycles, policy decisions, approvals, verification results, and immutable audit records.

## Input boundary

- Consumes: `investigation.completed.v1`
- Input must be completed-investigation context (snapshot + recommendation context)
- No raw event ingestion
- No direct evidence stream consumption

## Output topics

- `execution.plan.created.v1`
- `execution.policy.checked.v1`
- `execution.awaiting.approval.v1`
- `execution.approved.v1`
- `execution.ready.v1`
- `execution.started.v1`
- `execution.completed.v1`
- `execution.failed.v1`
- `execution.cancelled.v1`
- `execution.verified.v1`
- `execution.audit.v1`

## Deterministic guarantees

- Stable task ordering by deterministic sort keys
- Policy and approval decisions are reproducible from the same input and configuration
- No probabilistic decisions, no AI, no external calls for decision logic
- Full execution traceability through immutable audit records

## Security and scope limits

- No connector execution logic
- No external enterprise system mutation
- No service bypass of policy/approval pipeline
- Tenant isolation required for all plan/task/audit records

## Persistence

- Current implementation: in-memory repository for plans, tasks, queue, history, and audit
- Designed for future persistence adapter without changing domain/application logic
