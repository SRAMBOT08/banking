# ServiceNow Model Design

This document describes the purpose and lifecycle of the ServiceNow pipeline
data models.

## IncidentRequest

### Why it exists

`IncidentRequest` is the internal business request emitted by the planner. It
represents the canonical input before any ServiceNow request-body normalization
or execution planning occurs.

### Producer

- Future planner logic
- Future incident normalization layer

### Consumer

- `IncidentPayload` builder
- Pipeline orchestration

### Lifecycle

1. Created from upstream intent.
2. Passed into the payload builder or incident business layer.
3. Transformed into a normalized payload for execution.

## IncidentPayload

### Why it exists

`IncidentPayload` is the execution-ready representation of an incident request.
It closely matches the structure that the table executor will eventually send to
ServiceNow while remaining internal to Hermes.

### Producer

- `payload_builder.py`
- `incidents.py`

### Consumer

- `table_executor.py`
- `pipeline.py`

### Lifecycle

1. Built from an `IncidentRequest`.
2. Passed into the table executor.
3. Used as the execution input for incident creation or update.

## ExecutionResult

### Why it exists

`ExecutionResult` captures the outcome of the table executor. It records the
minimal execution facts needed by later verification and persistence layers.

### Producer

- `table_executor.py`
- future API or browser executor implementations

### Consumer

- `verifier.py`
- `pipeline.py`
- `store.py`

### Lifecycle

1. Returned after execution.
2. Passed to verification if required.
3. Persisted as execution metadata or terminal result.

## VerificationResult

### Why it exists

`VerificationResult` records whether the pipeline successfully confirmed the
incident creation result.

### Producer

- `verifier.py`

### Consumer

- `pipeline.py`
- `store.py`

### Lifecycle

1. Produced after execution completes.
2. Used to determine whether the pipeline is terminally successful.
3. Stored as part of the execution record.

