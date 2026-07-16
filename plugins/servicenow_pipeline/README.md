# ServiceNow Pipeline

## Purpose

`servicenow_pipeline` is the Hermes capability that creates ServiceNow incidents through the existing Hermes plugin and runtime architecture.

The MVP use case is:

- Accept an internal incident request
- Normalize it into a ServiceNow payload
- Execute the table create request
- Verify the result

## Architecture

The capability follows a thin orchestration model:

`IncidentRequest -> PayloadBuilder -> TableExecutor -> IncidentService -> ExecutionVerifier -> ServiceNowPipeline`

Supporting layers:

- `servicenow_client.py` handles ServiceNow transport and session management
- `table_executor.py` provides generic CRUD operations for ServiceNow tables
- `payload_builder.py` normalizes internal requests into ServiceNow payloads
- `incidents.py` coordinates incident creation
- `verifier.py` validates execution success
- `runtime.py` wires the components into Hermes startup

## Folder Structure

| File | Role |
|---|---|
| `__init__.py` | Plugin registration entry point |
| `plugin.yaml` | Hermes plugin manifest |
| `runtime.py` | Startup wiring and dependency composition |
| `pipeline.py` | ServiceNow pipeline orchestration |
| `models.py` | Internal request/result dataclasses |
| `incidents.py` | Incident orchestration layer |
| `payload_builder.py` | Payload normalization and transformation |
| `table_executor.py` | Generic ServiceNow table CRUD executor |
| `servicenow_client.py` | Generic ServiceNow HTTP client |
| `verifier.py` | MVP execution verification |
| `store.py` | Future persistence scaffold |
| `cli.py` | Operator-facing CLI scaffold |

## How to Configure

Create a local `.env` file from `.env.example` and set:

```bash
SERVICENOW_INSTANCE_URL=https://<your-instance>.service-now.com
SERVICENOW_USERNAME=<your-username>
SERVICENOW_PASSWORD=<your-password>
SERVICENOW_VERIFY_SSL=true
SERVICENOW_TIMEOUT=30
SERVICENOW_LOG_LEVEL=INFO
```

The smoke test also reads `~/.hermes/.env` if present.

## How to Run

1. Prepare the environment:

```bash
bash scripts/setup_servicenow.sh
```

2. Validate the environment:

```bash
python scripts/check_environment.py
```

3. Run the first incident smoke test:

```bash
python scripts/test_create_incident.py
```

## How to Test

For the current MVP, the primary test is the smoke script:

- [`scripts/test_create_incident.py`](/Users/user/hermes/hermes-agent/scripts/test_create_incident.py)

This script composes the real ServiceNow client, executor, payload builder, incident service, verifier, and pipeline.

## Known Limitations

- The capability currently targets incident creation first.
- Reference resolution is intentionally deferred.
- Verification is lightweight and checks only the MVP success criteria.
- The local environment must provide valid ServiceNow credentials and Hermes dependencies.

## Future Roadmap

- Expand the business layer for additional ServiceNow operations
- Add richer verification for post-create validation
- Add persistence for job tracking and replay
- Extend the same architecture to change, problem, CMDB, knowledge, and catalog workflows

