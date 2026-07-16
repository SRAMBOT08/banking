# Phase 2 Capability Lifecycle

This document traces one complete capability execution lifecycle for the Teams Pipeline plugin.

Scope:

- Teams Pipeline only
- Start at `plugin.yaml`
- Follow the runtime execution path through completion
- No Hermes CLI, AIAgent, tool registry, or unrelated repository flows

## Capability Overview

The Teams Pipeline is a standalone plugin that wires Microsoft Teams meeting ingestion into a durable pipeline:

- Plugin discovery loads the manifest and plugin entrypoint
- Gateway runtime binds the plugin to the Teams webhook adapter
- The plugin creates `TeamsMeetingPipeline`
- The pipeline resolves meetings, fetches transcript or recording artifacts, summarizes content, and writes sink outputs
- Durable state is recorded in the local Teams pipeline store

---

## 1. Plugin Registration

| File | Function / Object | Responsibility | Next Component |
|---|---|---|---|
| `plugins/teams_pipeline/plugin.yaml` | manifest | Declares the plugin identity, version, description, platform scope, and that it is a standalone plugin. | Plugin discovery |
| `plugins/teams_pipeline/__init__.py` | `register(ctx)` | Registers the plugin as an operator-facing CLI capability. The manifest does not load runtime behavior by itself. | Plugin loader |

### What the manifest contributes

`plugin.yaml` is the declarative capability descriptor. It identifies:

- `name: teams_pipeline`
- `kind: standalone`
- target platforms
- metadata for discovery and presentation

It does not execute the pipeline. It only makes the plugin discoverable.

---

## 2. How the Plugin Is Discovered

| File | Function | Responsibility | Next Component |
|---|---|---|---|
| `hermes_cli/plugins.py` | `discover_plugins()` | Starts plugin discovery across bundled, user, project, and entry-point plugin sources. | Manifest scanning |
| `hermes_cli/plugins.py` | `_scan_directory()` / `_scan_directory_level()` | Locates `plugin.yaml` files beneath plugin directories. | Manifest parsing |
| `hermes_cli/plugins.py` | `_parse_manifest()` | Parses `plugin.yaml` into an internal `PluginManifest`. | Plugin module import |
| `hermes_cli/plugins.py` | `_load_plugin()` | Imports the plugin package and calls its `register(ctx)` entrypoint. | Plugin registration |

### Discovery path for Teams Pipeline

The Teams Pipeline lives under the bundled plugin tree:

`plugins/teams_pipeline/`

The plugin loader scans the bundled plugins directory, finds `plugins/teams_pipeline/plugin.yaml`, parses the manifest, and then imports the package to invoke its `register(ctx)` function from `plugins/teams_pipeline/__init__.py`.

---

## 3. How `plugin.yaml` Is Parsed

| File | Function | Responsibility | Next Component |
|---|---|---|---|
| `hermes_cli/plugins.py` | `_scan_directory_level()` | Detects `plugin.yaml` or `plugin.yml` in a plugin directory. | Manifest parse |
| `hermes_cli/plugins.py` | `_parse_manifest()` | Reads the manifest text and converts it into structured plugin metadata. | Plugin import / registration |

### Parse outcome

The manifest is converted into a `PluginManifest` object containing:

- plugin name
- version
- description
- author
- kind
- source location
- path
- capability metadata

For Teams Pipeline, the parsed manifest marks the plugin as standalone and keeps it in the bundled plugin namespace.

---

## 4. How `runtime.py` Is Loaded

| File | Function | Responsibility | Next Component |
|---|---|---|---|
| `gateway/run.py` | runtime binding path around `bind_gateway_runtime()` | Imports `plugins.teams_pipeline.runtime` when the gateway initializes Teams platform support. | `bind_gateway_runtime()` |
| `plugins/teams_pipeline/runtime.py` | module import | Defines runtime wiring helpers but does not instantiate the pipeline on import alone. | Gateway runtime binding |

### Important distinction

`runtime.py` is not the same as plugin discovery.

- Discovery loads the plugin package and registers the CLI capability.
- The gateway later imports `plugins.teams_pipeline.runtime` when it needs to attach the Teams Pipeline to the webhook adapter.

---

## 5. Who Creates `TeamsMeetingPipeline`

| File | Function | Responsibility | Next Component |
|---|---|---|---|
| `plugins/teams_pipeline/runtime.py` | `build_pipeline_runtime(gateway)` | Creates the operational pipeline instance for the gateway runtime. | `TeamsMeetingPipeline(...)` |
| `plugins/teams_pipeline/cli.py` | `_cmd_run(args)` | Creates a pipeline instance for CLI replay of a stored job. | `TeamsMeetingPipeline(...)` |

### Construction sites

`TeamsMeetingPipeline` is instantiated in two places:

- Gateway runtime binding via `build_pipeline_runtime(gateway)`
- CLI replay via `_cmd_run(args)`

For the live capability path, the gateway runtime is the primary creator.

---

## 6. Who Injects Dependencies

| File | Function | Responsibility | Next Component |
|---|---|---|---|
| `plugins/teams_pipeline/runtime.py` | `build_pipeline_runtime(gateway)` | Injects the graph client, persistent store, runtime config, and optional Teams sender into the pipeline constructor. | `TeamsMeetingPipeline(...)` |
| `plugins/teams_pipeline/cli.py` | `_cmd_run(args)` | Injects a graph client, store, and empty config for replaying an existing job. | `TeamsMeetingPipeline(...)` |
| `plugins/teams_pipeline/pipeline.py` | `TeamsMeetingPipeline.__init__()` | Accepts the injected dependencies and normalizes the config object. | Job execution methods |

### Dependency set

For gateway execution, `build_pipeline_runtime()` supplies:

- `graph_client` from `build_graph_client()`
- `store` from `TeamsPipelineStore(resolve_teams_pipeline_store_path())`
- `config` from `build_pipeline_runtime_config(gateway.config)`
- `teams_sender` when Teams delivery is configured and available

The pipeline also defaults `transcribe_fn` and `summarize_fn` internally when they are not injected.

---

## 7. Who Calls `run_job()`

| File | Function | Responsibility | Next Component |
|---|---|---|---|
| `plugins/teams_pipeline/runtime.py` | `bind_gateway_runtime(gateway)` | Installs the schedule callback on the webhook adapter so inbound notifications are routed to the pipeline. | `runtime.run_notification(notification)` |
| `plugins/teams_pipeline/runtime.py` | `_schedule(notification, event)` | Awaits `runtime.run_notification(notification)` for each inbound Graph notification. | `TeamsMeetingPipeline.run_notification()` |
| `plugins/teams_pipeline/pipeline.py` | `run_notification(notification)` | Converts a raw Graph notification into a job and then starts execution. | `run_job(job.job_id)` |
| `plugins/teams_pipeline/cli.py` | `_cmd_run(args)` | Replays a stored job from the CLI path. | `pipeline.run_job(job_id)` |

### Primary live path

For the live capability path, `run_job()` is called after:

1. Gateway binds the Teams runtime
2. The webhook adapter receives a Graph notification
3. The scheduled callback invokes `runtime.run_notification(notification)`
4. The pipeline creates or resolves a job
5. The pipeline calls `run_job(...)`

---

## 8. How `meetings.py` Is Invoked

| File | Function | Responsibility | Next Component |
|---|---|---|---|
| `plugins/teams_pipeline/pipeline.py` | `run_job()` | Coordinates meeting resolution, transcript lookup, fallback recording handling, and call-record enrichment. | Meeting helper functions |
| `plugins/teams_pipeline/meetings.py` | `resolve_meeting_reference()` | Resolves the meeting object from Microsoft Graph. | Meeting ref normalization |
| `plugins/teams_pipeline/meetings.py` | `fetch_preferred_transcript_text()` | Selects and downloads the preferred transcript when available. | Transcript text |
| `plugins/teams_pipeline/meetings.py` | `list_recording_artifacts()` | Lists recordings when transcript fallback is required. | Recording selection |
| `plugins/teams_pipeline/meetings.py` | `download_recording_artifact()` | Downloads the chosen recording artifact for transcription fallback. | Local transcription step |
| `plugins/teams_pipeline/meetings.py` | `enrich_meeting_with_call_record()` | Adds call-record data when available. | Summary payload construction |

### Meeting helper role

`meetings.py` is the Graph-facing helper layer. It keeps Graph-specific resolution and artifact handling separate from the pipeline orchestration itself.

---

## 9. How `store.py` Participates

| File | Function | Responsibility | Next Component |
|---|---|---|---|
| `plugins/teams_pipeline/runtime.py` | `build_pipeline_runtime()` | Creates the durable store instance passed into the pipeline. | `TeamsPipelineStore(...)` |
| `plugins/teams_pipeline/store.py` | `resolve_teams_pipeline_store_path()` | Resolves the JSON-backed store location. | Store initialization |
| `plugins/teams_pipeline/store.py` | `TeamsPipelineStore.__init__()` | Loads durable state from disk into memory. | Job/subscription/sink record access |
| `plugins/teams_pipeline/store.py` | `upsert_job()` | Persists job lifecycle state. | Updated job record |
| `plugins/teams_pipeline/store.py` | `get_job()` / `list_jobs()` | Reads job state for execution replay and dedupe. | Pipeline job coercion |
| `plugins/teams_pipeline/store.py` | `record_notification_receipt()` | Stores notification receipt dedupe state. | Duplicate suppression |
| `plugins/teams_pipeline/store.py` | `upsert_sink_record()` | Persists output sink results. | Durable sink state |

### Store role in the lifecycle

The store participates at every stage:

- deduplicates notifications
- persists job status transitions
- stores summary and sink outputs
- makes replay and inspection possible

---

## 10. How Results Are Returned

| File | Function | Responsibility | Next Component |
|---|---|---|---|
| `plugins/teams_pipeline/pipeline.py` | `run_job()` | Returns the final `TeamsMeetingPipelineJob` after completion or failure handling. | Caller |
| `plugins/teams_pipeline/runtime.py` | `_schedule(notification, event)` | Awaits the pipeline execution and completes the notification lifecycle. | Gateway adapter |
| `plugins/teams_pipeline/cli.py` | `_cmd_run(args)` | Prints the final job JSON after replay execution. | CLI operator |
| `plugins/teams_pipeline/store.py` | `upsert_job()` / `upsert_sink_record()` | Commits the durable final state used by later inspection. | Subsequent reads |

### Result shape

The final result is a `TeamsMeetingPipelineJob` object whose stored state includes:

- `status`
- `meeting_ref`
- `summary_payload`
- `error_info` when applicable
- sink record updates

That object is also serialized into the store so later runs, inspections, and replays can see the completed lifecycle.

---

## 11. Complete Execution Sequence

```text
plugins/teams_pipeline/plugin.yaml
  ↓
hermes_cli/plugins.py:discover_plugins()
  ↓
hermes_cli/plugins.py:_scan_directory_level()
  ↓
hermes_cli/plugins.py:_parse_manifest()
  ↓
hermes_cli/plugins.py:_load_plugin()
  ↓
plugins/teams_pipeline/__init__.py:register(ctx)
  ↓
gateway/run.py runtime startup
  ↓
gateway/run.py imports plugins.teams_pipeline.runtime
  ↓
plugins/teams_pipeline/runtime.py:bind_gateway_runtime(gateway)
  ↓
plugins/teams_pipeline/runtime.py:build_pipeline_runtime(gateway)
  ↓
plugins/teams_pipeline/pipeline.py:TeamsMeetingPipeline(...)
  ↓
gateway webhook adapter receives Microsoft Graph notification
  ↓
plugins/teams_pipeline/runtime.py:_schedule(notification, event)
  ↓
plugins/teams_pipeline/pipeline.py:run_notification(notification)
  ↓
plugins/teams_pipeline/pipeline.py:create_job_from_notification(notification)
  ↓
plugins/teams_pipeline/store.py:record_notification_receipt()
  ↓
plugins/teams_pipeline/store.py:upsert_job()
  ↓
plugins/teams_pipeline/pipeline.py:run_job(job_id)
  ↓
plugins/teams_pipeline/meetings.py:resolve_meeting_reference()
  ↓
plugins/teams_pipeline/meetings.py:fetch_preferred_transcript_text()
  ↓
plugins/teams_pipeline/meetings.py:list_recording_artifacts()
  ↓
plugins/teams_pipeline/meetings.py:download_recording_artifact()
  ↓
tools/transcription_tools.py:transcribe_audio()
  ↓
plugins/teams_pipeline/meetings.py:enrich_meeting_with_call_record()
  ↓
plugins/teams_pipeline/pipeline.py:_generate_summary_payload()
  ↓
agent/auxiliary_client.py:async_call_llm()
  ↓
plugins/teams_pipeline/pipeline.py:_write_sinks()
  ↓
plugins/teams_pipeline/store.py:upsert_sink_record()
  ↓
plugins/teams_pipeline/store.py:upsert_job(status="completed")
  ↓
final TeamsMeetingPipelineJob returned
```

---

## 12. Execution Summary by Responsibility

| Question | Answer |
|---|---|
| How is the plugin discovered? | The plugin loader scans bundled plugin directories, finds `plugins/teams_pipeline/plugin.yaml`, parses it, and imports the package to call `register(ctx)`. |
| How is `plugin.yaml` parsed? | `hermes_cli/plugins.py` reads the manifest text with a safe YAML loader and converts it into `PluginManifest`. |
| How is `runtime.py` loaded? | It is imported later by the gateway runtime when Teams support is being bound, not during manifest parsing. |
| Who creates `TeamsMeetingPipeline`? | `plugins/teams_pipeline/runtime.py:build_pipeline_runtime()` creates it for live gateway execution, and `plugins/teams_pipeline/cli.py:_cmd_run()` creates it for replay. |
| Who injects dependencies? | `build_pipeline_runtime()` injects the graph client, store, config, and optional sender. |
| Who calls `run_job()`? | `runtime.run_notification()` calls it for live events; `_cmd_run()` calls it for CLI replay. |
| How is `meetings.py` invoked? | `run_job()` calls the Graph helper functions during meeting resolution, transcript retrieval, recording fallback, and call-record enrichment. |
| How does `store.py` participate? | It stores notification receipts, job state transitions, and sink results, and provides replay/read access. |
| How are results returned? | `run_job()` returns the final `TeamsMeetingPipelineJob`, and the caller either forwards it into gateway completion or prints it in CLI replay. |

