# ServiceNow Architecture Audit

## Executive Summary

The ServiceNow MVP implementation is architecturally coherent and largely follows the intended layering:

`Hermes Runtime -> ServiceNow Runtime -> Pipeline -> Incident Service -> Payload Builder -> Table Executor -> ServiceNow Client -> ServiceNow REST API`

The dependency direction is mostly correct and downward-only. The codebase cleanly separates transport, CRUD abstraction, payload normalization, orchestration, and verification. The runtime wiring in `gateway/run.py` also follows the Teams pattern closely enough that ServiceNow now participates in Hermes startup.

No critical architectural break was found that requires an immediate code change before declaring the MVP complete.

## Architecture Diagram

```text
Hermes Runtime
   |
   v
ServiceNow Runtime
   |
   v
ServiceNowPipeline
   |
   v
IncidentService
   |
   v
PayloadBuilder
   |
   v
TableExecutor
   |
   v
ServiceNowClient
   |
   v
ServiceNow REST API
```

## Dependency Diagram

```text
gateway/run.py
  -> plugins.servicenow_pipeline.runtime
    -> plugins.servicenow_pipeline.pipeline
      -> plugins.servicenow_pipeline.incidents
        -> plugins.servicenow_pipeline.payload_builder
        -> plugins.servicenow_pipeline.table_executor
          -> plugins.servicenow_pipeline.servicenow_client
      -> plugins.servicenow_pipeline.verifier
```

## Module Review

### `plugins/servicenow_pipeline/__init__.py`

- Purpose: plugin registration entry point.
- Architectural layer: plugin integration.
- Strengths:
  - Keeps Hermes plugin discovery compatible with the standard `register(ctx)` pattern.
  - Avoids business logic.
- Weaknesses:
  - Registers only a placeholder CLI surface; it does not itself wire runtime startup.
- Notes:
  - This is acceptable because runtime binding is handled in `gateway/run.py`.

### `plugins/servicenow_pipeline/plugin.yaml`

- Purpose: manifest for plugin discovery and activation.
- Architectural layer: configuration.
- Strengths:
  - Correct standalone plugin metadata.
  - Compatible with Hermes plugin scanning.
- Weaknesses:
  - Minimal metadata only; this is fine for MVP.

### `plugins/servicenow_pipeline/runtime.py`

- Purpose: compose ServiceNow dependencies into a ready runtime object.
- Architectural layer: runtime initialization.
- Strengths:
  - Correct dependency direction.
  - Builds client, executor, payload builder, incident service, verifier, then pipeline.
  - Reads configuration without contacting ServiceNow.
- Weaknesses:
  - Imports `ServiceNowPipelineStore` even though the current runtime path does not use persistence. This is dead-code coupling, not a runtime blocker.
  - Uses a store helper name that is Teams-compatible in shape but ServiceNow-specific in behavior; acceptable, but slightly confusing.
- Verdict:
  - Architecturally sound.

### `plugins/servicenow_pipeline/pipeline.py`

- Purpose: thin orchestration layer.
- Architectural layer: runtime orchestration.
- Strengths:
  - Properly delegates to `IncidentService` and `ExecutionVerifier`.
  - No HTTP, CRUD, or payload logic.
- Weaknesses:
  - `execute()` catches `IncidentServiceError` and `VerificationError` into a generic verification failure, which is fine for MVP but collapses error detail somewhat.
- Verdict:
  - Correct and appropriately thin.

### `plugins/servicenow_pipeline/incidents.py`

- Purpose: incident workflow orchestration.
- Architectural layer: business orchestration.
- Strengths:
  - Correctly owns request validation, payload preparation, creation execution, and result shaping.
  - No transport logic.
- Weaknesses:
  - `create_incident()` currently uses a TODO placeholder for reference resolution, which is intentional and not blocking the MVP.
  - `process_result()` assumes success once the table executor returns a record; final acceptance is deferred to the verifier.
- Verdict:
  - Good separation of concerns.

### `plugins/servicenow_pipeline/payload_builder.py`

- Purpose: normalize internal incident requests into ServiceNow payloads.
- Architectural layer: transformation.
- Strengths:
  - Pure transformation, deterministic, side-effect free.
  - Keeps assignment group and caller as human-readable values.
- Weaknesses:
  - No lookup resolution yet, by design.
- Verdict:
  - Correct boundary.

### `plugins/servicenow_pipeline/table_executor.py`

- Purpose: generic CRUD abstraction for ServiceNow tables.
- Architectural layer: infrastructure adapter.
- Strengths:
  - Table-agnostic.
  - CRUD methods are generic and parameterized by table name.
  - Properly translates client transport failures into executor-level errors.
- Weaknesses:
  - Some helper methods return structured wrappers while the creation path still has to infer record IDs from response shape.
  - The executor exposes several wrapper dataclasses that are not yet used by the ServiceNow MVP flow, which is fine but slightly increases surface area.
- Verdict:
  - Clean and reusable.

### `plugins/servicenow_pipeline/servicenow_client.py`

- Purpose: ServiceNow transport boundary.
- Architectural layer: infrastructure/client.
- Strengths:
  - Owns session lifecycle, headers, timeout handling, SSL configuration, and response normalization.
  - Supports environment-based configuration.
  - Keeps credentials out of code.
  - No incident-specific knowledge.
- Weaknesses:
  - Retry policy is modeled but not actively applied inside the client.
  - Error normalization is centralized, but `requests`-specific transport behavior is still visible through the implementation choice.
- Verdict:
  - Good MVP transport boundary, with retry behavior left for future hardening.

### `plugins/servicenow_pipeline/verifier.py`

- Purpose: determine whether an execution completed successfully.
- Architectural layer: business verification.
- Strengths:
  - Lightweight and intentionally narrow.
  - Validates the MVP criteria: success, incident number, sys_id, and message.
- Weaknesses:
  - Future verification hooks are documented as TODOs, which is expected.
- Verdict:
  - Correct for MVP.

### `plugins/servicenow_pipeline/models.py`

- Purpose: internal datamodels shared across the capability.
- Architectural layer: domain contract.
- Strengths:
  - Frozen dataclasses.
  - Clear request, payload, execution, and verification stages.
- Weaknesses:
  - None material.
- Verdict:
  - Solid contract layer.

### `plugins/servicenow_pipeline/store.py`

- Purpose: persistence scaffold.
- Architectural layer: infrastructure/persistence.
- Strengths:
  - Keeps future persistence isolated.
  - Does not leak into current execution flow.
- Weaknesses:
  - Not used by the MVP path.
  - Still scaffold-level and intentionally non-functional.
- Verdict:
  - Acceptable dead-end for now because the MVP does not require persistence.

## Supporting Files

### `gateway/run.py`

- Purpose: Hermes gateway startup and lifecycle.
- ServiceNow relevance:
  - Adds a ServiceNow enablement check.
  - Binds the ServiceNow runtime during startup.
- Review:
  - This mirrors the Teams integration pattern closely enough for startup participation.
  - Dependency direction remains correct: gateway wires runtime, but runtime does not reach back into gateway logic.

### `scripts/test_create_incident.py`

- Purpose: standalone smoke test for first incident creation.
- Review:
  - Correctly composes the ServiceNow capability with the real modules.
  - Loads dotenv from repo root and `~/.hermes/.env`.
  - Could provide earlier failure messages for missing packages or env vars, but current behavior is acceptable.

### `scripts/check_environment.py`

- Purpose: validation gate for local readiness.
- Review:
  - Useful and appropriately narrow.
  - Confirms Python version, imports, env vars, and instance URL format.

### `scripts/setup_servicenow.sh`

- Purpose: reproducible onboarding entry point.
- Review:
  - Good developer experience.
  - Uses `uv` and verifies dependencies.

### `docs/`

- Purpose: architecture and onboarding documentation.
- Review:
  - Documentation coverage is strong.
  - The ServiceNow docs are aligned with the implementation and do not describe a different architecture than the code actually uses.

## Strengths

- Clear layered architecture with downward dependency flow.
- Good separation between transport, CRUD, transformation, orchestration, and verification.
- Hermes startup wiring now follows the existing plugin integration pattern.
- Generic client and executor can support future ServiceNow tables without redesign.
- Payload transformation is deterministic and side-effect free.
- The smoke-test and setup flow are documented and reproducible.

## Weaknesses

- Persistence is scaffold-only and not yet part of the MVP path.
- Retry policy is modeled but not yet fully exercised in the client.
- Some runtime imports and persistence scaffolding are present but unused in the incident-only flow.
- The verification model is intentionally lightweight, which is correct for MVP but will be insufficient for stronger post-create guarantees later.

## Technical Debt

- `ServiceNowPipelineStore` is present but not used.
- `retry_policy` exists as configuration but is not yet implemented as active retry behavior.
- Future reference resolution is explicitly deferred.
- Future post-create verification beyond ID presence is deferred.

## Recommended Improvements

### Critical

- None identified for the current MVP architecture review.

### Recommended

- Implement real retry execution around transient ServiceNow failures when the product needs stronger resilience.
- Add a future persistence path only when job replay or audit requirements become real.
- Expand verifier coverage when the incident lifecycle needs post-create confirmation.

### Optional

- Reduce unused imports in runtime modules if the persistence layer remains unused for an extended period.
- Enhance smoke-test diagnostics for dependency and configuration failures.

## Production Risks

- A live ServiceNow call can still fail due to credentials, instance availability, or network configuration.
- Retry semantics are not yet applied in the client, so transient failures may fail fast.
- Future changes to ServiceNow response shapes may require tighter response mapping.

## Future Readiness

The current architecture can support additional ServiceNow capabilities without major refactoring:

- Update Incident
- Query Incident
- Close Incident
- Change Management
- Problem Management
- CMDB
- Knowledge
- Catalog

Why this works:

- The client is generic.
- The table executor is generic.
- The payload builder is isolated.
- The incident service is a domain-specific orchestration layer that can be mirrored by new services.
- The pipeline is thin and can be extended or paralleled by additional capability pipelines.

## Scores

| Category | Score |
|---|---:|
| Architecture | 9/10 |
| Maintainability | 8.5/10 |
| Extensibility | 9/10 |
| Security | 8.5/10 |
| Overall Engineering | 8.7/10 |

## Final Assessment

The ServiceNow MVP implementation is structurally sound, follows the intended architecture, and is ready for the next phase of live operational validation.

