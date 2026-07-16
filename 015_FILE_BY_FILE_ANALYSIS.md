# File-by-File Analysis

## Core Files

### `hermes_bootstrap.py`
- Performs Windows UTF-8 bootstrap and import-path hardening.
- Also activates the durable lazy-install path when configured.

### `run_agent.py`
- Main agent runtime entrypoint.
- Loads env/config, initializes the model loop, tool system, and execution flow.

### `model_tools.py`
- Thin orchestration layer over the tool registry.
- Imports tool modules, discovers plugins, and exposes tool metadata/functions.

### `tools/registry.py`
- Central tool registry and discovery layer.
- Holds tool schemas, handlers, check functions, and toolset maps.

### `agent/memory_provider.py`
- Abstract memory-provider interface.
- Defines the lifecycle contract for external memory backends.

### `agent/memory_manager.py`
- Runtime integration point for memory providers.
- Manages prompt injection, prefetch, sync, and tool exposure.

### `hermes_cli/plugins.py`
- Plugin loader and lifecycle manager.
- Discovers bundled/user/project/pip plugins and invokes plugin hooks.

### `gateway/run.py`
- Gateway entrypoint for platform adapters and long-lived messaging sessions.

### `gateway/session.py`
- Session metadata model and routing helpers.

### `gateway/platform_registry.py`
- Registry for platform adapters.
- Supports deferred loading and plugin-owned adapter registration.

### `plugins/teams_pipeline/*`
- Standalone example plugin for a Teams pipeline runtime.
- Includes manifest, entrypoint, runtime wiring, CLI, storage, and domain helpers.

## Unable to Verify

A complete file-by-file analysis for every important file in the repository would be much longer than this file and was not fully completed here.

> Unable to verify from the current codebase.
