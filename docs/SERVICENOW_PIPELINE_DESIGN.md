# ServiceNow Pipeline Design

## Purpose

The ServiceNow pipeline is the thin orchestration layer for the capability. It
coordinates incident execution and verification without owning transport,
payload mapping, CRUD behavior, or ServiceNow response semantics.

## Responsibilities

- orchestrate the incident workflow
- delegate execution to `IncidentService`
- delegate verification to `ExecutionVerifier`
- normalize failures into a terminal verification result
- keep the public orchestration interface stable

## Dependency Graph

```text
Caller
  ↓
ServiceNowPipeline
  ├── IncidentService
  └── ExecutionVerifier
```

## Execution Flow

```text
execute()
  ↓
IncidentService.create_incident()
  ↓
ExecutionVerifier.verify_creation()
  ↓
VerificationResult
```

## Current MVP

The MVP pipeline is intentionally thin:

- no HTTP
- no payload transformation
- no CRUD implementation
- no verification logic beyond the verifier layer
- no runtime integration

## Future Evolution

TODO insertion points are reserved for:

- Capability Router
- Multiple Operations
- Workflow Engine
- Human Approval
- Retry Policy
- Audit Logging

## Design Notes

- The pipeline does not know ServiceNow REST details.
- Business logic remains in `IncidentService`.
- Verification remains in `ExecutionVerifier`.
- Failures are normalized to a terminal `VerificationResult` instead of
  exposing lower-level exceptions to callers.

