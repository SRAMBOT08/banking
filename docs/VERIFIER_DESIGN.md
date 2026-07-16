# Verifier Design

## Purpose

The verifier determines whether a ServiceNow execution completed successfully.
It is intentionally narrow and exists so the pipeline can have a stable,
lightweight confirmation layer without coupling verification to transport or
business logic.

## Responsibilities

- validate the execution result shape
- check MVP-required identifiers
- produce a terminal verification result
- preserve a public interface that can grow later

## Verification Flow

```text
ExecutionResult
  ↓
verify_response()
  ↓
verify_required_fields()
  ↓
build_verification_result()
  ↓
VerificationResult
```

## Current MVP Scope

The MVP verifier only checks:

- `success` is true
- `sys_id` is present
- `incident_number` is present
- the execution message is present

No additional ServiceNow calls are made.

## Future Enhancements

TODO insertion points are reserved for:

- reference validation
- post-create GET verification
- business rule verification
- SLA verification
- attachment verification
- audit log verification
- retry verification

## Integration Points

| Component | Role |
|---|---|
| `ExecutionResult` | Input from the executor layer |
| `VerificationResult` | Terminal confirmation output |
| `pipeline.py` | Future orchestration consumer |

## Design Notes

- The public verifier interface stays stable.
- The implementation is lightweight for the MVP.
- No HTTP calls are performed.
- No ServiceNow client exceptions are exposed.
- No record mutation or lookup logic is included.

