# ServiceNow Execution Adapter (Phase 9 MVP)

Deterministic adapter that consumes approved execution tasks and executes **only ServiceNow REST operations**.

## Supported operations

- `CREATE_INCIDENT`
- `GET_INCIDENT`
- `UPDATE_INCIDENT`
- `LOOKUP_USER`
- `LOOKUP_CMDB_CI`
- `CREATE_CHANGE_REQUEST`

## Contracts

### Consumes

- `execution.ready.v1`

### Publishes

- `execution.started.v1`
- `execution.completed.v1`
- `execution.failed.v1`
- `execution.verified.v1`

## Endpoints

- `GET /health`
- `POST /dry-run`
- `POST /execute`

## Security and governance

- HTTPS-only ServiceNow URL.
- Credentials from environment variables only.
- Secret-masked structured JSON logs.
- Immutable append-only audit log with hash chaining.
- Deterministic idempotency key propagation via execution ID.
