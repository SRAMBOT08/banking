# Live Execution Trace

## Purpose

This document defines the observability contract for the ServiceNow MVP
`Create Incident` path. The goal is to make the first live execution easy to
diagnose without changing the architecture or the business flow.

## Execution Stages

The first incident execution now emits trace data at these stages:

1. Runtime Initialization
2. Pipeline Execution
3. `IncidentService.create_incident()`
4. `PayloadBuilder.build_incident_payload()`
5. `TableExecutor.create_record()`
6. `ServiceNowClient.request()`
7. HTTP Response
8. `ExecutionVerifier.verify_creation()`
9. Pipeline Completion

## Correlation ID Flow

Every execution carries a single `correlation_id` through the entire path.

Flow:

`scripts/test_create_incident.py`
→ `ServiceNowPipeline.execute_create_incident(...)`
→ `IncidentService.create_incident(...)`
→ `PayloadBuilder.build_incident_payload(...)`
→ `TableExecutor.create_record(...)`
→ `ServiceNowClient.request(...)`
→ HTTP response
→ `ExecutionVerifier.verify_creation(...)`
→ pipeline completion

The same ID appears in all stage logs and in the smoke-test console output.

## Logging Conventions

Each trace event includes:

- `stage`
- `correlation_id`
- `success`
- `duration_ms`
- `message` when useful
- `error_type`, `error_message`, and `stack_trace` on failures

Sensitive values are masked or omitted:

- passwords
- access tokens
- authorization headers
- raw credentials

## Example Log Output

```text
2026-07-16 10:32:11,120 INFO plugins.servicenow_pipeline.runtime ServiceNow trace: {"component": "servicenow_pipeline", "correlation_id": "7fd4f6e3b4bf4e5d8edcc1f0d9f7f2a0", "duration_ms": 3.41, "message": "Runtime initialization", "stage": "runtime_initialization", "success": true}
2026-07-16 10:32:15,004 INFO plugins.servicenow_pipeline.pipeline ServiceNow trace: {"component": "servicenow_pipeline", "correlation_id": "7fd4f6e3b4bf4e5d8edcc1f0d9f7f2a0", "duration_ms": 0.0, "message": "Incident pipeline handoff started", "stage": "pipeline_execution", "success": true}
2026-07-16 10:32:15,005 INFO plugins.servicenow_pipeline.incidents ServiceNow trace: {"correlation_id": "7fd4f6e3b4bf4e5d8edcc1f0d9f7f2a0", "duration_ms": 0.0, "message": "Incident workflow started", "stage": "incident_service", "success": true, "request": {"short_description": "Hermes MVP Test Incident", "description": "This incident was created during the first end-to-end integration validation of the ServiceNow Claw.", "priority": "3", "urgency": "3", "impact": "3", "category": "hardware", "assignment_group": "Network Team", "caller": "hermes"}}
2026-07-16 10:32:15,007 INFO plugins.servicenow_pipeline.servicenow_client ServiceNow trace: {"correlation_id": "7fd4f6e3b4bf4e5d8edcc1f0d9f7f2a0", "duration_ms": 0.0, "message": "HTTP request prepared", "stage": "servicenow_request", "success": true, "method": "POST", "endpoint": "/api/now/table/incident", "timeout": 30.0, "verify_ssl": true}
2026-07-16 10:32:15,842 INFO plugins.servicenow_pipeline.servicenow_client ServiceNow trace: {"correlation_id": "7fd4f6e3b4bf4e5d8edcc1f0d9f7f2a0", "duration_ms": 835.21, "stage": "http_response", "success": true, "method": "POST", "endpoint": "/api/now/table/incident", "status_code": 200, "response": {"result": {"sys_id": "f2c1...", "number": "INC0012345"}}}
2026-07-16 10:32:15,844 INFO plugins.servicenow_pipeline.verifier ServiceNow trace: {"correlation_id": "7fd4f6e3b4bf4e5d8edcc1f0d9f7f2a0", "duration_ms": 1.26, "message": "Verification completed", "stage": "verification", "success": true, "verified": true}
2026-07-16 10:32:15,844 INFO __main__ ServiceNow trace: {"correlation_id": "7fd4f6e3b4bf4e5d8edcc1f0d9f7f2a0", "duration_ms": 840.83, "message": "Smoke test completed", "stage": "pipeline_completion", "success": true, "incident_number": "INC0012345", "sys_id": "f2c1...", "verified": true}
```

## Failure Diagnosis Guide

When the first live execution fails, use the last successful stage in the log
stream to isolate the break:

### Failure Before Runtime Initialization

- Likely cause: plugin import or startup wiring issue
- Check: `gateway/run.py`, plugin enablement, runtime imports

### Failure During `IncidentService.create_incident()`

- Likely cause: request validation or orchestration error
- Check: input request fields, payload preparation, executor exception

### Failure During `PayloadBuilder.build_incident_payload()`

- Likely cause: invalid internal request data
- Check: input normalization and required fields

### Failure During `TableExecutor.create_record()`

- Likely cause: table request construction or ServiceNow client error
- Check: table name, payload shape, request path

### Failure During `ServiceNowClient.request()`

- Likely cause: network, auth, timeout, or ServiceNow response problem
- Check: endpoint, auth config, SSL, timeout, response status

### Failure During `ExecutionVerifier.verify_creation()`

- Likely cause: ServiceNow created a record but the response is missing
  required identifiers
- Check: `sys_id`, incident number, and success flag in the response

## What Not to Log

Do not emit:

- passwords
- tokens
- authorization headers
- raw secret environment values
- any other credential material

## Operational Use

For the first live incident test, start with:

```bash
python scripts/test_create_incident.py
```

Then inspect:

- the correlation ID
- the last successful stage
- any failure stage-specific stack trace
- the ServiceNow HTTP status and sanitized response body

