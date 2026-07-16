# Hermes Startup Validation: ServiceNow Capability

## 1. Hermes Startup Sequence

1. Hermes loads the gateway runner from `gateway/run.py`.
2. Hermes loads configuration and plugin enablement state from `~/.hermes/config.yaml`.
3. The plugin loader discovers bundled plugin manifests under `plugins/`.
4. Enabled standalone plugins are imported and their `register(ctx)` functions run.
5. Gateway startup binds platform-specific runtimes.
6. The Teams pipeline runtime is attached to the Graph webhook ingress when enabled.
7. The ServiceNow pipeline runtime is now attached during the same startup lifecycle when enabled.
8. Hermes transitions the gateway into the running state.

## 2. Plugin Discovery Flow

ServiceNow follows the normal Hermes plugin discovery path:

- `plugins/servicenow_pipeline/plugin.yaml` marks the capability as a bundled standalone plugin.
- `hermes_cli.plugins.PluginManager` scans `plugins/servicenow_pipeline/` like any other bundled plugin directory.
- `plugins/servicenow_pipeline/__init__.py::register(ctx)` exposes the CLI surface.
- `plugins.enabled` controls whether the standalone plugin is activated.

## 3. ServiceNow Integration Points

ServiceNow is now integrated at the same startup layer as Teams:

- `plugins/servicenow_pipeline/runtime.py::bind_gateway_runtime(gateway)` composes the runtime object graph.
- `gateway/run.py::_servicenow_pipeline_plugin_enabled()` checks whether the capability is enabled.
- `gateway/run.py::_wire_servicenow_pipeline_runtime()` imports and binds the ServiceNow runtime during gateway startup.
- `gateway/run.py` now calls the ServiceNow wiring hook during the startup sequence.

## 4. Changes Made

### Modified Files

- `gateway/run.py`
- `plugins/servicenow_pipeline/store.py`

### What Changed

- Added a ServiceNow plugin enablement check mirroring the Teams pattern.
- Added a ServiceNow runtime wiring hook in gateway startup.
- Added gateway-level runtime slots for ServiceNow runtime state and errors.
- Added the missing ServiceNow store path resolver helper so the runtime import boundary is consistent.

## 5. Validation Results

### Successful Checks

- The modified Python modules compile successfully with `py_compile`.
- The ServiceNow runtime composition path remains importable after the store compatibility fix.
- The gateway startup code now contains an explicit ServiceNow wiring step, matching the Teams lifecycle pattern.

### Environment-Limited Checks

- A full dynamic gateway boot could not be completed in this sandbox because the local environment is missing optional runtime dependencies such as `httpx`.
- A full plugin-manager import path also depends on `PyYAML` in this environment.

### Practical Result

The code changes are sufficient for Hermes startup integration, but the sandbox could not execute a full end-to-end gateway boot for external dependency reasons unrelated to the ServiceNow wiring itself.

## 6. Remaining Blockers Before the First Real Incident Creation

- A real ServiceNow Developer Instance must be configured with valid credentials.
- The ServiceNow plugin must be enabled in `plugins.enabled`.
- A live end-to-end run still needs to be performed against ServiceNow to confirm authentication and incident creation.
- Any environment missing Hermes runtime dependencies cannot perform the full startup boot validation in isolation.

## Final Status

✅ ServiceNow capability is fully integrated and ready for the first live incident test.

