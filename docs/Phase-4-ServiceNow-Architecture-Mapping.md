# Phase 4 ServiceNow Architecture Mapping

Scope:

- `plugins/teams_pipeline/plugin.yaml`
- `plugins/teams_pipeline/runtime.py`
- `plugins/teams_pipeline/pipeline.py`
- `plugins/teams_pipeline/models.py`
- `plugins/teams_pipeline/meetings.py`
- `plugins/teams_pipeline/store.py`
- `plugins/teams_pipeline/cli.py`

Target MVP use case:

- Create Incident

This document maps the existing Teams Pipeline architecture to a ServiceNow Pipeline architecture without redesigning Hermes.

---

## 1. Mapping Overview

The migration philosophy is to preserve the execution framework and replace the Teams-specific business semantics.

### Component disposition

| Decision | Meaning in this migration |
|---|---|
| `KEEP` | The component is structurally reusable without changing its architectural role |
| `MODIFY` | The component remains, but its responsibilities, data model, or dependencies change |
| `REPLACE` | The component’s role stays useful, but the implementation must become ServiceNow-specific |
| `REMOVE` | The component has no meaningful place in the MVP and should disappear from the ServiceNow path |

### Migration stance

- Keep the durable orchestration skeleton.
- Modify runtime wiring to bind a ServiceNow adapter instead of Microsoft Graph.
- Replace the Teams meeting business layer with incident-oriented business logic.
- Replace transcript/recording summary steps with request preparation, execution selection, and verification steps.
- Remove Teams-only sink behavior and Graph-specific assumptions.

---

## 2. Component Mapping Table

| Current Component | Current Responsibility | ServiceNow Equivalent | Migration Strategy | Complexity | Risk |
|---|---|---|---|---|---|
| `TeamsMeetingPipeline` | Orchestrates notification-to-summary execution | `ServiceNowPipeline` | `MODIFY` | High | High |
| `TeamsPipelineConfig` | Normalizes Teams pipeline configuration | `ServiceNowPipelineConfig` | `MODIFY` | Medium | Medium |
| `TeamsMeetingPipelineJob` | Durable job record for pipeline execution | `ExecutionJob` | `MODIFY` | High | Medium |
| `TeamsMeetingRef` | Normalized meeting reference | `IncidentRequest` | `REPLACE` | Medium | Medium |
| `MeetingArtifact` | Transcript/recording/call-record artifact metadata | `ExecutionPayload` | `REPLACE` | Medium | Medium |
| `TeamsMeetingSummaryPayload` | Structured summary output | `ExecutionResult` | `REPLACE` | High | Medium |
| `run_notification()` | Notification entrypoint | `run_request()` or equivalent | `MODIFY` | High | High |
| `create_job_from_notification()` | Converts Graph notifications into jobs | `create_job_from_incident_request()` | `REPLACE` | High | High |
| `_transcribe_recording()` | Audio fallback execution | `api_executor` / `browser_executor` stage | `REPLACE` | High | High |
| `_generate_summary_payload()` | Produces summary from transcript | `payload_builder` + result builder | `REPLACE` | High | High |
| `_write_sinks()` | Writes to Notion/Linear/Teams | ServiceNow incident update / verification output | `MODIFY` | High | High |
| `NotionWriter` | Notion sink adapter | Remove or replace with ServiceNow sink | `REMOVE` / `REPLACE` | Medium | Medium |
| `LinearWriter` | Linear sink adapter | Remove or replace with ServiceNow sink | `REMOVE` / `REPLACE` | Medium | Medium |
| `meetings.py` | Graph meeting resolution helpers | `incidents.py` and request helpers | `REPLACE` | High | High |
| `store.py` | Durable local job and sink state | `store.py` for ServiceNow executions | `MODIFY` | Medium | Medium |
| `runtime.py` | Gateway runtime binding | ServiceNow runtime binding | `MODIFY` | Medium | Medium |
| `cli.py` | Operator CLI for Teams pipeline | ServiceNow operator CLI | `MODIFY` | Medium | Medium |
| `plugin.yaml` | Teams plugin manifest | ServiceNow plugin manifest | `MODIFY` | Low | Low |

### Example mapping

| Teams concept | ServiceNow concept |
|---|---|
| `TeamsMeetingPipeline` | `ServiceNowPipeline` |
| `MeetingArtifact` | `IncidentPayload` |
| `TeamsMeetingRef` | `IncidentRequest` |
| `TeamsMeetingSummaryPayload` | `ExecutionResult` |

---

## 3. Folder Mapping

### Current to target folder mapping

| Current Folder/File | Target Folder/File | Action |
|---|---|---|
| `plugins/teams_pipeline/` | `plugins/servicenow_pipeline/` | New folder |
| `plugin.yaml` | `plugin.yaml` | Modify |
| `runtime.py` | `runtime.py` | Modify |
| `pipeline.py` | `pipeline.py` | Modify |
| `models.py` | `models.py` | Modify |
| `meetings.py` | `incidents.py` / supporting business layer | Replace |
| `store.py` | `store.py` | Modify |
| `cli.py` | `cli.py` | Modify |

### File-level disposition

| File | Reuse | Modify | Replace | Remove | New |
|---|---|---|---|---|---|
| `plugin.yaml` | metadata structure | platform/service metadata | - | - | - |
| `runtime.py` | runtime binding pattern | dependency injection, adapter target | - | - | - |
| `pipeline.py` | orchestration skeleton | all Teams-specific stages | execution stages | - | - |
| `models.py` | normalized model pattern | fields and semantics | Teams entities | - | new ServiceNow models |
| `meetings.py` | - | - | incident business logic layer | Teams Graph layer | `incidents.py`, `payload_builder.py`, etc. |
| `store.py` | durable state container | job metadata and logs | Teams sink records | - | execution logs/verification results |
| `cli.py` | CLI registration pattern | commands and arguments | Teams command verbs | Teams-only commands | ServiceNow command verbs |

---

## 4. Execution Flow Mapping

### Current Teams flow

```text
Graph Notification
↓
Meeting Resolution
↓
Transcript / Recording
↓
Summary Generation
↓
Sink Writing
↓
Completed
```

### ServiceNow MVP flow

```text
ServiceNow Trigger / Request
↓
Incident Request Normalization
↓
Execution Planning
↓
Payload Building
↓
Execution Selection
↓
API Execution or Browser Execution
↓
Verification
↓
Persistence
↓
Completed
```

### Complete ServiceNow execution sequence

```text
plugin.yaml
↓
plugin discovery
↓
runtime.py binding
↓
ServiceNowPipeline construction
↓
request received
↓
job created
↓
request normalized into IncidentRequest
↓
payload_builder prepares incident payload
↓
execution_selector chooses API or browser path
↓
api_executor or browser_executor performs action
↓
verifier checks result
↓
store persists job + execution metadata
↓
result returned
```

---

## 5. Data Model Mapping

| Teams Model | ServiceNow Model | Why |
|---|---|---|
| `TeamsMeetingRef` | `IncidentRequest` | Both represent the normalized primary unit of work that starts the pipeline |
| `MeetingArtifact` | `ExecutionPayload` | Both carry the raw input artifact or source material needed to drive execution |
| `TeamsMeetingPipelineJob` | `ExecutionJob` | Both are durable execution records that move through states |
| `TeamsMeetingSummaryPayload` | `ExecutionResult` | Both are the final structured output of the pipeline |
| `GraphSubscription` | `TriggerRegistration` or `RequestSubscription` | Both represent remote subscription state if the ServiceNow path uses event-driven intake |

### Model rationale

- `IncidentRequest` replaces meeting reference because the pipeline’s primary object is no longer a meeting, but an incident creation request.
- `ExecutionPayload` replaces meeting artifacts because the pipeline may now consume request text, attachments, field mappings, and context data.
- `ExecutionResult` replaces summary output because the final product is not a meeting summary but a durable incident operation result.

---

## 6. Runtime Mapping

### What stays

- Plugin discovery contract
- Dependency injection pattern
- Gateway binding pattern
- Durable pipeline construction
- CLI/operator entrypoint pattern

### What changes

- Teams runtime binding becomes ServiceNow runtime binding
- Graph client construction becomes ServiceNow client construction
- Teams sender selection becomes ServiceNow-specific sink selection
- Teams config assembly becomes ServiceNow config assembly

### What gets injected

- ServiceNow API client
- store instance
- pipeline config
- optional browser executor
- optional verifier
- optional CLI/operator callback surfaces

### What gets removed

- Microsoft Graph-specific adapter binding
- Teams delivery writer
- Graph subscription management from the live path
- Teams webhook assumptions

---

## 7. Pipeline Mapping

### Reusable orchestration

- job creation
- job coercion
- persistence checkpoints
- terminal state handling
- durable replay
- dependency injection boundary

### New orchestration

- incident request normalization
- execution planning
- payload building
- execution selection
- API/browser execution branching
- verification

### Removed orchestration

- meeting resolution
- transcript selection
- recording fallback
- call-record enrichment
- Teams sink fan-out

### New execution stages

| New Stage | Purpose |
|---|---|
| `normalizing_request` | Convert incoming ServiceNow input into a canonical incident request |
| `building_payload` | Prepare the request for execution |
| `selecting_execution_path` | Choose API or browser mode |
| `executing_api` | Use ServiceNow API to create the incident |
| `executing_browser` | Use browser automation if API is unavailable or insufficient |
| `verifying_result` | Confirm incident creation succeeded |
| `persisting_result` | Store final execution metadata |

---

## 8. Business Logic Mapping

`meetings.py` should be replaced by a ServiceNow business logic layer that separates domain logic from orchestration.

### New business layer

| Module | Responsibility |
|---|---|
| `incidents.py` | Normalize ServiceNow incident inputs and resolve field semantics |
| `payload_builder.py` | Build canonical incident payloads from incoming requests |
| `execution_selector.py` | Decide whether API or browser execution should be used |
| `api_executor.py` | Create or update incidents using ServiceNow APIs |
| `browser_executor.py` | Drive browser-based fallback or UI-based workflows |
| `verifier.py` | Validate that the incident was created successfully and record verification evidence |

### Interaction model

```text
IncidentRequest
↓
incidents.py
↓
payload_builder.py
↓
execution_selector.py
↓
api_executor.py or browser_executor.py
↓
verifier.py
↓
ExecutionResult
```

### Responsibility split

- `incidents.py` owns domain normalization.
- `payload_builder.py` owns execution input construction.
- `execution_selector.py` owns strategy selection.
- `api_executor.py` owns API interaction.
- `browser_executor.py` owns UI-driven fallback interaction.
- `verifier.py` owns success validation and proof capture.

---

## 9. Persistence Mapping

`store.py` should remain the durable state boundary, but its payloads and metadata must change.

### Reusable job lifecycle

- create
- update
- retrieve
- list
- dedupe
- terminal state marking

### New execution metadata

| Metadata | Purpose |
|---|---|
| incident number | Identity of the created incident |
| request source | Origin of the request |
| execution mode | API or browser |
| selector decision | Why a path was chosen |
| runtime evidence | What proof was captured |

### Verification results

- verifier status
- verification timestamp
- verification notes
- evidence payload

### Execution logs

- stage transitions
- API responses
- browser actions
- retry and failure details

---

## 10. Plugin Mapping

### `plugin.yaml`

Change:

- name from Teams Pipeline to ServiceNow Pipeline
- description to incident creation use case
- capability metadata to ServiceNow scope

### CLI registration

Change:

- Teams-focused operator commands
- add ServiceNow-oriented commands for incident creation, job inspection, replay, and verification review

### Runtime registration

Change:

- gateway binding target from Teams webhook adapter to ServiceNow event/source adapter
- client construction from Graph to ServiceNow

### Capability metadata

Change:

- Graph subscription metadata
- Teams delivery metadata
- meeting pipeline fields

Replace with:

- ServiceNow instance metadata
- credential scope
- incident workflow configuration
- execution mode defaults

---

## 11. New Folder Structure

### Target structure

```text
plugins/servicenow_pipeline/
├── __init__.py
├── plugin.yaml
├── runtime.py
├── pipeline.py
├── models.py
├── store.py
├── cli.py
├── incidents.py
├── payload_builder.py
├── execution_selector.py
├── api_executor.py
├── browser_executor.py
├── verifier.py
└── README.md
```

### File purpose

| File | Purpose |
|---|---|
| `__init__.py` | Plugin registration entrypoint |
| `plugin.yaml` | Plugin manifest |
| `runtime.py` | Gateway/runtime binding |
| `pipeline.py` | Execution orchestration engine |
| `models.py` | Execution models and payload types |
| `store.py` | Durable state |
| `cli.py` | Operator commands |
| `incidents.py` | Incident normalization and domain logic |
| `payload_builder.py` | Build canonical execution payloads |
| `execution_selector.py` | Choose API vs browser execution |
| `api_executor.py` | ServiceNow API execution |
| `browser_executor.py` | Browser fallback execution |
| `verifier.py` | Result validation |
| `README.md` | Capability documentation |

---

## 12. Migration Roadmap

### Phase 1: Copy Teams Pipeline

Deliverable:

- New `plugins/servicenow_pipeline/` folder created by cloning the Teams structure
- No behavior change yet

### Phase 2: Rename Components

Deliverable:

- Teams names replaced with ServiceNow names
- Manifest, CLI verbs, runtime identifiers, and models renamed

### Phase 3: Replace Business Logic

Deliverable:

- `meetings.py` replaced by incident-oriented modules
- Graph-specific helpers removed from the execution path

### Phase 4: Implement ServiceNow Execution

Deliverable:

- Incident creation via API and browser fallback
- Verification flow implemented
- Result persistence added

### Phase 5: Verification

Deliverable:

- End-to-end execution proves incident creation
- Job state and verification evidence are persisted

### Phase 6: Cleanup

Deliverable:

- Teams-only code removed from the ServiceNow pipeline
- Dead fields and unused sink paths eliminated

---

## 13. MVP Readiness

### Advantages

- The existing pipeline already provides a durable execution skeleton.
- Dependency injection is already in place.
- The architecture already separates orchestration from domain helpers.
- Replay and persistence patterns already exist.
- The pipeline already supports fallback and verification-style branching patterns.

### Limitations

- The current implementation is strongly Teams/Graph oriented.
- Existing data models encode meeting concepts, not incident concepts.
- The current summary and sink behavior does not match incident creation semantics.
- Verification is implicit or sink-oriented, not a dedicated incident proof flow.

### Technical risks

- Overfitting the new pipeline to Teams-specific state shapes.
- Reusing the wrong persistence fields and carrying meeting semantics forward.
- Mixing ServiceNow API logic directly into orchestration.
- Keeping sink abstractions that do not fit incident creation.

### Expected effort

- Moderate to high
- The orchestration frame is reusable, but the business layer must change substantially
- The safest path is to preserve the job lifecycle skeleton and replace the domain engine

---

## Summary View

### Keep

- orchestration skeleton
- lifecycle persistence pattern
- runtime injection boundary
- replayable job model

### Modify

- runtime binding
- data models
- config shape
- store payloads
- CLI verbs

### Replace

- Graph/meeting helpers
- summary generation semantics
- sink adapters
- Teams-specific execution stages

### Remove

- Teams-only outbound delivery paths
- Graph subscription handling from the ServiceNow MVP path
- meeting-specific artifacts and terminology

