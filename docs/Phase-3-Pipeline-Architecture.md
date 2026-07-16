# Phase 3 Pipeline Architecture

Scope: `plugins/teams_pipeline/pipeline.py`

Minimal supporting references used only where necessary:

- `plugins/teams_pipeline/models.py`
- `plugins/teams_pipeline/store.py`
- `plugins/teams_pipeline/meetings.py`
- `plugins/teams_pipeline/runtime.py`

---

## 1. Pipeline Purpose

The Teams Pipeline exists to turn Microsoft Graph meeting notifications into durable, transcript-first meeting summaries and downstream sink writes.

### Primary responsibility

It owns the execution lifecycle for one meeting-processing job:

- accept or recover a job
- resolve the meeting
- gather transcript or recording input
- produce a structured summary payload
- write results to configured sinks
- persist every meaningful state transition

### Why runtime delegates to it

The runtime layer needs a small boundary object that can be:

- constructed with injected dependencies
- called from a webhook notification path
- reused by CLI replay
- isolated from adapter-specific wiring

`TeamsMeetingPipeline` is that execution boundary. The runtime binds transport and configuration; the pipeline owns orchestration.

---

## 2. Pipeline Architecture

### Major components

| Component | Responsibility | Type |
|---|---|---|
| `TeamsMeetingPipeline` | Orchestrates job execution from notification to completion | Execution engine |
| `TeamsPipelineConfig` | Normalizes runtime configuration | Configuration model |
| `NotionWriter` | Writes summary payloads to Notion | Sink adapter |
| `LinearWriter` | Writes summary payloads to Linear | Sink adapter |
| `TeamsPipelineError` family | Classifies failure behavior | Control/error taxonomy |

### Internal helper roles

| Helper / Method Group | Role |
|---|---|
| job creation and dedupe helpers | Convert notifications into durable job records |
| job coercion helpers | Rehydrate jobs from IDs or existing objects |
| persistence helpers | Write intermediate and terminal state to the store |
| transcription helpers | Handle fallback from transcript to recording |
| summary generation helpers | Build structured meeting summaries |
| sink writing helpers | Deliver summary output to configured destinations |

### Component diagram

```text
                    +----------------------+
Notification -----> | TeamsMeetingPipeline  |
                    +----------------------+
                              |
                              v
        +---------------------+----------------------+
        |                                           |
        v                                           v
 +---------------------+                   +----------------------+
 | Meeting Resolution  |                   | Persistent Store     |
 | meetings.py         |                   | store.py             |
 +---------------------+                   +----------------------+
        |                                           ^
        v                                           |
 +---------------------+                   +----------------------+
 | Artifact Fetching    |                   | Job / Sink Records   |
 | transcript/recording |                   +----------------------+
 +---------------------+
        |
        v
 +---------------------+
 | Summary Generation  |
 | local/LLM fallback  |
 +---------------------+
        |
        v
 +---------------------+     +--------------------+
 | Sink Writing        |---->| Notion / Linear /  |
 |                     |     | Teams delivery     |
 +---------------------+     +--------------------+
```

---

## 3. Pipeline Lifecycle

### End-to-end execution

```text
Pipeline created
↓
Notification received or job replay requested
↓
Job created or loaded from store
↓
Meeting reference resolved
↓
Transcript attempted
↓
Recording fallback used if needed
↓
Call record enrichment
↓
Summary generated
↓
Configured sinks written
↓
Job marked terminal
↓
Final job returned
```

### Lifecycle stages

| Stage | What Happens | Output |
|---|---|---|
| Pipeline created | Runtime injects client, store, config, and optional sink writers | Ready-to-run pipeline instance |
| Notification received | Raw Graph event becomes pipeline input | Notification payload |
| Job created | Notification is deduplicated and converted into a job | `TeamsMeetingPipelineJob` |
| Validation | Meeting reference is checked and required data is present | Resolved meeting target or failure |
| Execution | Transcript/recording/call-record handling and summarization run | Summary payload |
| Persistence | Each stage writes status and data into the store | Durable job state |
| Completion | Job is finalized as completed, retry_scheduled, or failed | Terminal job record |

---

## 4. Internal State Machine

### States

| State | Meaning | Entry Condition | Exit Condition | Transition Rules |
|---|---|---|---|---|
| `received` | Job exists but has not started orchestration | Notification converted into a job | `run_job()` begins | Only flows forward into active execution or terminal return for already-terminal jobs |
| `resolving_meeting` | Graph meeting resolution in progress | Execution starts | Meeting ref resolved or failure occurs | Must precede any artifact retrieval |
| `fetching_transcript` | Preferred transcript lookup is active | Transcript-first path is enabled | Transcript found or unavailable | Can lead to summary path or recording fallback |
| `downloading_recording` | Recording fallback is active | No acceptable transcript is available | Recording selected or failure occurs | Only entered when transcript path fails or is disabled |
| `transcribing_audio` | Local transcription is running | Recording downloaded and audio prepared | STT returns transcript or fails | Only used in fallback path |
| `summarizing` | Summary generation is in progress | Transcript text is available | Summary payload built | Occurs before sink writes |
| `writing_notion` | Notion sink write is in progress | Notion sink enabled and writer present | Sink write succeeds or fails | Sink-specific terminal substate |
| `writing_linear` | Linear sink write is in progress | Linear sink enabled and writer present | Sink write succeeds or fails | Sink-specific terminal substate |
| `sending_teams` | Teams delivery sink is in progress | Teams delivery enabled and sender present | Sink write succeeds or fails | Sink-specific terminal substate |
| `completed` | Job finished successfully | All required execution steps complete | Terminal | No further processing unless explicitly replayed |
| `retry_scheduled` | Retryable failure occurred | A retryable exception was raised | Terminal in store, retryable externally | No automatic in-process retry loop inside the pipeline |
| `failed` | Non-retryable failure occurred | Unexpected exception raised | Terminal | Execution ends immediately |

### State transition diagram

```text
received
  ↓
resolving_meeting
  ↓
fetching_transcript ──no transcript──> downloading_recording
  ↓                                   ↓
summarizing <──── transcribing_audio ──┘
  ↓
writing_notion
  ↓
writing_linear
  ↓
sending_teams
  ↓
completed

Any active state
  ├─ retryable exception → retry_scheduled
  └─ unexpected exception → failed
```

---

## 5. Job Lifecycle

### Creation

A job is created from a Graph notification. The notification is deduplicated using a receipt key, then converted into a job model carrying:

- event identity
- source event type
- dedupe key
- meeting reference
- initial status

### Evolution

The job is updated at each phase boundary:

- meeting resolution
- transcript retrieval
- fallback recording download
- transcription
- summary generation
- sink writes
- terminal completion or failure

### Updates

Job updates are persisted via a store-backed replacement pattern:

- the in-memory job object is updated
- a merged payload is written to the store
- the stored record is rehydrated back into the job model

This makes persistence part of the orchestration flow, not an afterthought.

### Completion

A successful job ends with:

- `summary_payload` populated
- sink records stored
- status set to `completed`

### Failure handling

The job ends in one of two terminal failure states:

- `retry_scheduled` for retryable operational conditions
- `failed` for non-retryable errors

---

## 6. Pipeline Responsibilities

### Responsibilities that belong inside the pipeline

| Responsibility | Why it belongs here |
|---|---|
| Orchestration | The pipeline is the execution engine for one meeting job |
| Job lifecycle management | It owns state transitions and persistence checkpoints |
| Meeting resolution | It decides when and how meeting input is acquired |
| Fallback policy | It chooses transcript-first vs recording STT fallback |
| Summary assembly | It controls summary generation and payload shaping |
| Sink coordination | It routes output to configured destinations |
| Retry classification | It decides whether a failure is retryable or terminal |

### Responsibilities that should not live here

| Responsibility | Why it should stay elsewhere |
|---|---|
| Transport binding | Belongs in `runtime.py` and adapter wiring |
| Graph client construction | Belongs in runtime / subscription helpers |
| Store implementation | Belongs in `store.py` |
| Graph artifact mechanics | Belongs in `meetings.py` |
| Plugin discovery | Belongs in the plugin loader |

---

## 7. Dependency Analysis

| Dependency | Class | Why it exists |
|---|---|---|
| `httpx` | External | Used by sink writers for API calls |
| `agent.auxiliary_client.async_call_llm` | Internal | Used to generate the summary payload when available |
| `agent.auxiliary_client.extract_content_or_reasoning` | Internal | Extracts model output for summary parsing |
| `hermes_constants.get_hermes_home` | Infrastructure | Resolves temp and durable filesystem locations |
| `plugins.teams_pipeline.meetings` | Internal / business logic | Resolves meetings and fetches artifacts |
| `plugins.teams_pipeline.models` | Internal | Supplies normalized job, meeting, and payload data models |
| `plugins.teams_pipeline.store` | Infrastructure | Persists and reloads job/sink state |
| `tools.transcription_tools.transcribe_audio` | Business logic / infrastructure bridge | Performs audio transcription fallback |
| `asyncio`, `shutil`, `tempfile`, `uuid`, `pathlib` | Infrastructure | Manage concurrency, local filesystem work, and temp artifacts |

### Dependency classification

- Internal: `meetings.py`, `models.py`, `store.py`, auxiliary client helpers
- External: `httpx`
- Infrastructure: filesystem, temp directories, `asyncio`, `shutil`
- Business logic: transcription and summarization invocation points

---

## 8. Orchestration Analysis

`pipeline.py` is the conductor, not the transport layer.

### Orchestration model

- `runtime.py` injects the ready-to-use pipeline instance.
- `run_notification()` converts a webhook event into a job and decides whether execution should proceed.
- `run_job()` sequences the actual lifecycle.
- `meetings.py` is called when Graph-specific work is needed.
- `store.py` is called whenever job state or sink state must become durable.

### How business logic is invoked

The pipeline invokes business logic in three major blocks:

1. Meeting acquisition
2. Summary generation
3. Sink writing

The actual data handling is delegated out to specialized helpers and writers rather than being embedded in the pipeline itself.

### How `meetings.py` is called

The pipeline calls meeting helpers for:

- resolving the meeting reference
- reading transcript artifacts
- enumerating recordings
- downloading a recording
- enriching with call record metadata

### How `store.py` is called

The store is used for:

- deduplication receipts
- job persistence
- sink record persistence
- job lookup / replay support

### How `runtime.py` communicates with it

`runtime.py` constructs the pipeline, then binds a callback so the gateway can pass notifications into `run_notification()`.

---

## 9. Error Handling

### Retry strategy

- Retryable failures are converted to `retry_scheduled`.
- The pipeline does not spin an internal retry loop.
- Retry intent is expressed through job status and error metadata.

### Exception handling

| Exception path | Result |
|---|---|
| Retryable pipeline error | Stored as `retry_scheduled` |
| Any other exception | Stored as `failed` |

### Failure recovery

Recovery is mostly external to the pipeline:

- later retry by the hosting system
- replay via CLI
- reprocessing a newer notification

### Rollback behavior

There is no transactional rollback across Graph fetch, transcription, summary generation, and sink writes. The pipeline prefers incremental persistence over all-or-nothing rollback.

### Partial completion handling

Partial progress is preserved:

- if meeting resolution succeeds but summary fails, the store still contains the earlier states
- if one sink fails after another has succeeded, prior sink records remain persisted

### Timeout handling

The pipeline itself does not define a dedicated timeout policy. Timeout behavior is delegated to:

- async call boundaries
- Graph client behavior
- transcription tooling
- sink client behavior

---

## 10. Persistence Flow

### When state is persisted

State is persisted at these points:

- when a notification receipt is recorded
- when a job is created
- when a job state changes
- when a summary payload is produced
- when sink output is written
- when the final job terminal state is reached

### When jobs are updated

Jobs are updated after every meaningful transition:

- meeting resolution
- transcript selection
- fallback selection
- transcription
- summary generation
- sink writes
- terminal status

### How replay works

Replay works by:

- loading a persisted job from the store
- coercing it back into a `TeamsMeetingPipelineJob`
- calling `run_job(job_id)`

### How completed jobs are stored

Completed jobs remain in the JSON-backed store with:

- terminal status
- final meeting reference
- summary payload
- sink metadata
- timestamps

---

## 11. Extension Points

| Extension Point | Risk | Why |
|---|---|---|
| `transcribe_fn` injection | Safe | Pure dependency injection for fallback transcription |
| `summarize_fn` injection | Safe | Allows alternate summary generation without changing orchestration |
| `NotionWriter` / `LinearWriter` replacement | Moderate | Output contract must remain stable |
| `teams_sender` injection | Moderate | Output sink behavior must remain compatible |
| `_write_sinks()` branching | High Risk | Central delivery path; errors affect completion semantics |
| `run_job()` lifecycle sequencing | High Risk | Changes here alter the execution contract |
| `_generate_summary_payload()` | Moderate | Affects output semantics but not transport binding |
| `run_notification()` gating | High Risk | Controls whether work executes or is skipped |
| `TeamsPipelineConfig.from_dict()` | Moderate | Shapes all pipeline behavior and fallback policy |

### Safe extension rule

The safest extension points are dependency injections that preserve the current lifecycle ordering.

---

## 12. Generic vs Teams-Specific Logic

| Section of `pipeline.py` | Classification | Notes |
|---|---|---|
| `TeamsPipelineConfig` | Generic framework logic | Normalizes runtime configuration for a pipeline-style engine |
| Error classes | Generic framework logic | Classify execution control flow and sink failures |
| `TeamsMeetingPipeline.__init__()` | Generic framework logic | Dependency injection and orchestration setup |
| `create_job_from_notification()` | Teams-specific logic | Converts Microsoft Graph events into pipeline jobs |
| `run_notification()` | Generic framework logic | Standard notification-to-job handoff pattern |
| `run_job()` | Generic framework logic | Main execution engine pattern |
| Meeting resolution / transcript / recordings | Teams-specific logic | Microsoft Graph domain handling |
| Transcription fallback | Generic framework logic | Pattern is reusable across capabilities |
| Summary generation | Generic framework logic | The orchestration pattern is generic even though the content domain is Teams |
| Sink writing | Generic framework logic | Pluggable delivery pipeline pattern |
| `_generate_summary_payload()` | Teams-specific logic | Summary structure is meeting-summary oriented but content shape is domain-driven |
| `_write_sinks()` | Generic framework logic | Multi-sink dispatch pattern |
| Helper functions for artifacts and prompts | Teams-specific logic | Bound to Teams/Graph meeting semantics |

---

## 13. Keep / Modify / Replace Assessment

| Class / Method | Decision | Reason | Complexity | Risk | Dependencies |
|---|---|---|---|---|---|
| `TeamsMeetingPipeline` | KEEP | The orchestration boundary is the core asset | High | Medium | Store, Graph client, summarization, sinks |
| `TeamsPipelineConfig` | KEEP | Clean dependency normalization boundary | Low | Low | Runtime config |
| `TeamsPipelineError` hierarchy | KEEP | Useful execution taxonomy | Low | Low | None beyond pipeline semantics |
| `create_job_from_notification()` | KEEP | Encodes notification-to-job mapping | Medium | Medium | Store, meeting ref model |
| `run_notification()` | KEEP | Good adapter-friendly entrypoint | Low | Low | Job creation and runtime callback |
| `run_job()` | MODIFY | Core logic should be refactored only if the target capability needs a different domain pipeline | High | High | All pipeline dependencies |
| `_coerce_job()` | KEEP | Stable replay boundary | Low | Low | Store |
| `_find_job_by_dedupe_key()` | KEEP | Needed for notification dedupe | Medium | Medium | Store |
| `_persist_job()` | KEEP | Central persistence checkpoint | Medium | Medium | Store |
| `_transcribe_recording()` | MODIFY | Domain-agnostic fallback pattern is reusable, but the Teams recording flow is specific | Medium | Medium | Transcription tool, Graph artifacts |
| `_prepare_audio_path()` | KEEP | Generic media preparation support | Medium | Medium | FFmpeg, filesystem |
| `_generate_summary_payload()` | MODIFY | Summary strategy should remain pluggable | High | High | LLM client, heuristic fallback, payload model |
| `_write_sinks()` | MODIFY | Sink routing is reusable, but destination set is Teams-specific | High | High | Notion, Linear, Teams sender |
| `NotionWriter` | REPLACE | It is sink-specific and should not anchor a future ServiceNow pipeline | Medium | Medium | Notion API |
| `LinearWriter` | REPLACE | Same as above | Medium | Medium | Linear API |
| helper functions for artifact parsing | KEEP | Graph artifact handling is a stable domain layer | Medium | Medium | Meetings helpers |

### Summary of assessment

- Keep the execution skeleton.
- Modify the domain-specific meeting acquisition and sink branches.
- Replace sink adapters that are not relevant to a ServiceNow target.

---

## 14. ServiceNow Readiness Assessment

### Reusable unchanged

| Area | Why it can be reused |
|---|---|
| Job lifecycle skeleton | It already models create, run, persist, and finalize behavior |
| State persistence pattern | The store-backed durable job model is reusable |
| Retry classification | The retryable vs terminal split is useful for any pipeline |
| Dependency injection pattern | The pipeline already accepts injected client/writer functions |
| `_persist_job()` pattern | Useful as a durable checkpoint mechanism |
| `_coerce_job()` / replay pattern | Supports stored-job re-execution |

### Requires modification

| Area | Why it needs change |
|---|---|
| Meeting resolution path | Hard-coded to Microsoft Graph meeting semantics |
| Transcript / recording acquisition | Bound to Teams artifacts |
| Summary prompt shape | Built around Teams meeting data |
| Sinks | Notion, Linear, and Teams delivery are domain-specific targets |
| Call-record enrichment | Microsoft Graph-specific |

### Tightly coupled to Microsoft Teams

| Area | Coupling source |
|---|---|
| Notification ingestion | Graph notification shape |
| Meeting reference resolution | Microsoft Graph meeting endpoints |
| Transcript/recording lookup | Teams artifact model |
| Call-record enrichment | Microsoft Graph call record support |
| Teams delivery sink | Teams-specific outbound channel |

### Foundation for a ServiceNow pipeline

| Area | Why it is a good foundation |
|---|---|
| Pipeline orchestration skeleton | Already separates execution from transport and store setup |
| Job state machine | Already expresses a durable workflow lifecycle |
| Persistence checkpoints | Strong basis for auditable case/task workflows |
| Summary generation slot | Can be repurposed for case analysis, incident synthesis, or ticket notes |
| Sink interface pattern | Can be swapped for ServiceNow record updates and notifications |

---

## Architectural Bottom Line

`pipeline.py` is not just a helper module. It is the execution engine for a durable, notification-driven workflow.

Its strongest traits are:

- clear orchestration boundary
- injected dependencies
- durable progress tracking
- separable acquisition, summarization, and sink phases
- replayable job model

Its most Teams-specific parts are:

- Microsoft Graph meeting resolution
- transcript and recording retrieval
- call-record enrichment
- Teams outbound delivery

Those domain-specific sections are the parts that would need to change for a ServiceNow pipeline, while the orchestration skeleton itself is a strong candidate for reuse.

