# Hermes Plugin Integration Verification: ServiceNow

## Conclusion

❌ NOT FULLY INTEGRATED

The ServiceNow capability is discoverable and startup-wired, but it is not automatically enabled on a fresh clone because it is declared as a `standalone` plugin and the Hermes plugin loader only loads standalone plugins when they are present in `plugins.enabled`.

## 1. Startup Sequence Diagram

```text
Hermes Start
  |
  v
gateway/run.py loads config
  |
  v
Plugin discovery scans plugins/
  |
  v
ServiceNow plugin manifest found
  |
  v
Because kind=standalone, loader checks plugins.enabled
  |
  +--> if enabled: plugin module imported and register(ctx) called
  |
  +--> if not enabled: plugin skipped
  |
  v
Gateway startup continues
  |
  v
Gateway wires ServiceNow runtime only if plugin is enabled
  |
  v
Runtime composes client -> executor -> builder -> service -> verifier -> pipeline
  |
  v
Ready state
```

## 2. Plugin Loading Flow

### Evidence from `hermes_cli/plugins.py`

- Bundled plugins are scanned under `plugins/`.
- Standalone plugins are treated as opt-in.
- The loader only imports standalone plugins when:
  - the manifest key is in `plugins.enabled`, or
  - the legacy bare name is in `plugins.enabled`.

### Evidence from ServiceNow manifest

- `plugins/servicenow_pipeline/plugin.yaml`
  - `kind: standalone`
  - `name: servicenow_pipeline`

### Result

The plugin is discoverable, but not auto-enabled.

## 3. Runtime Initialization Flow

### Evidence from `gateway/run.py`

- `GatewayRunner._wire_servicenow_pipeline_runtime()` exists.
- It calls `bind_gateway_runtime(self)` only when `_servicenow_pipeline_plugin_enabled()` returns true.
- `_servicenow_pipeline_plugin_enabled()` checks `plugins.enabled`.

### Result

Runtime creation is automatic only after manual configuration enables the plugin.

## 4. Dependency Graph

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

## 5. Configuration Requirements

### Required for loading

- `plugins.enabled` must include:
  - `servicenow_pipeline`

### Required for execution

- `SERVICENOW_INSTANCE_URL`
- `SERVICENOW_USERNAME`
- `SERVICENOW_PASSWORD`

### Result

The plugin will not function as a native Hermes capability on a fresh clone unless `plugins.enabled` is updated.

## 6. Required Manual Steps

After cloning, a developer must manually:

1. Install dependencies.
2. Configure ServiceNow credentials.
3. Add `servicenow_pipeline` to `plugins.enabled`.

Without step 3, Hermes will discover the plugin but skip loading and runtime binding.

## 7. Missing Integration Points

- The plugin is not enabled by default.
- `plugin.yaml` declares `kind: standalone`, which makes auto-loading opt-in.
- Hermes startup does not override that default.

## 8. Answers with Evidence

1. Does Hermes automatically discover the ServiceNow plugin?
   - Yes. The plugin loader scans `plugins/` and will find `plugins/servicenow_pipeline/plugin.yaml`.

2. Is `plugin.yaml` correctly registered?
   - Yes. The manifest is parseable and compatible with Hermes plugin scanning.

3. Is `servicenow_pipeline` included in the plugin discovery path?
   - Yes. It is under the bundled `plugins/` tree scanned by Hermes.

4. Does Hermes instantiate ServiceNowRuntime during startup?
   - Only if the plugin is enabled in `plugins.enabled`.

5. Is ServiceNowPipeline created automatically?
   - Only if the plugin is enabled.

6. Are all dependencies composed automatically?
   - Only after the plugin is enabled.

7. Is the plugin enabled by default, or does configuration need to be changed?
   - Configuration must be changed. It is not enabled by default.

8. If I clone this repository onto a fresh machine and install dependencies, will Hermes automatically expose the ServiceNow capability?
   - No. The developer must still enable `servicenow_pipeline` in `plugins.enabled`.

9. Are there any hardcoded references that only support Teams?
   - The gateway startup wiring still has a Teams-specific pattern, but ServiceNow now has its own parallel hook. There is no blocker here for ServiceNow startup, only the opt-in plugin gate.

10. Are there any missing startup hooks?
    - No missing ServiceNow hook in code. The hook exists and is called from `gateway/run.py` when enabled.

11. Are there any missing configuration entries?
    - Yes. `plugins.enabled` must explicitly include `servicenow_pipeline`.

12. Are there any import path issues that would prevent loading?
    - No import-path blocker was found in the ServiceNow capability itself.

13. Are there any runtime compatibility issues?
    - No runtime compatibility blocker was found in the ServiceNow capability itself.

14. Is there anything that must be manually edited after cloning before ServiceNow will work?
    - Yes. `plugins.enabled` must be updated to include `servicenow_pipeline`, and ServiceNow credentials must be configured.

## 9. Simulated Startup Walkthrough

### Hermes Start

Hermes launches `gateway/run.py`.

### Plugin Discovery

Hermes scans `plugins/` and sees `plugins/servicenow_pipeline/plugin.yaml`.

### Plugin Registration

Hermes loads the manifest but does not import the module unless `servicenow_pipeline` is listed in `plugins.enabled`.

### Runtime Creation

If enabled, `gateway/run.py` calls `plugins.servicenow_pipeline.runtime.bind_gateway_runtime(self)`.

### Dependency Injection

`runtime.py` composes:

`ServiceNowClient -> TableExecutor -> PayloadBuilder -> IncidentService -> ExecutionVerifier -> ServiceNowPipeline`

### Pipeline Creation

`ServiceNowPipeline` is created as part of runtime composition.

### Capability Registration

The runtime is stored on the gateway instance and becomes available to the ServiceNow capability path.

### Ready State

Hermes continues startup with ServiceNow bound only if the plugin was enabled.

## Final Decision

❌ NOT FULLY INTEGRATED

### Exact Missing Integration Step

- `servicenow_pipeline` must be added to `plugins.enabled` for Hermes to load and expose the capability on a fresh clone.

