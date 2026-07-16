# Incident Service Design

## Purpose

The incident service is the orchestration layer for ServiceNow incident
operations. It coordinates validation, payload preparation, table execution,
and result processing without owning transport or payload mapping logic.

## Responsibilities

- coordinate the incident workflow
- perform minimal structural validation
- invoke the payload builder
- prepare the table executor input
- convert executor output into a terminal execution result
- reserve extension points for future reference resolution and verification

## Dependencies

| Dependency | Role |
|---|---|
| `PayloadBuilder` | Converts `IncidentRequest` into a normalized payload |
| `TableExecutor` | Performs the generic create operation |
| `IncidentRequest` | Input contract |
| `ExecutionResult` | Output contract |

## Execution Flow

```text
IncidentRequest
  ↓
validate_request()
  ↓
PayloadBuilder.build_incident_payload()
  ↓
TODO ReferenceResolver
  ↓
TableExecutor.create_record()
  ↓
process_result()
  ↓
ExecutionResult
```

## Future Integration Points

- reference resolver for lookup-backed fields
- verifier for post-execution confirmation
- persistence of orchestration metadata
- richer result enrichment after record creation

## Error Handling Strategy

- structural validation failures raise service-level validation errors
- payload builder failures are wrapped as orchestration errors
- table executor failures are wrapped as orchestration errors
- unexpected exceptions are converted into a service-level failure
- no HTTP details are exposed beyond the table executor boundary

## Design Notes

- The service is independent of Hermes runtime.
- It does not own HTTP or authentication.
- It does not own payload mapping.
- It does not implement verification.
- It keeps the workflow orchestration clean and insertion-friendly.

