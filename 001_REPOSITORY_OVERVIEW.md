# Repository Overview

This document summarizes the current Hermes repository structure based on the checked-in source.

## Top-Level Layout

| Path | Purpose |
| --- | --- |
| `run_agent.py` | Main agent runtime entrypoint and conversation loop. |
| `cli.py` | Interactive CLI entrypoint. |
| `gateway/` | Messaging gateway runtime and platform adapters. |
| `agent/` | Core agent subsystems: memory, prompts, retries, tool guardrails, usage, etc. |
| `tools/` | Built-in tool implementations and the tool registry. |
| `hermes_cli/` | CLI configuration, setup flows, plugin loader, and shared CLI infrastructure. |
| `plugins/` | Bundled plugins, including memory providers, model providers, platform integrations, and domain plugins. |
| `cron/` | Scheduler and cron job runtime. |
| `apps/shared/` | Shared web/desktop transport primitives. |
| `apps/desktop/` | Electron desktop client. |
| `ui-tui/` | Ink-based terminal UI. |
| `tui_gateway/` | Python JSON-RPC backend for the TUI. |
| `acp_adapter/` | ACP server integration. |
| `tests/` | Test suite. |

## Major Runtime Surfaces

| Surface | Entrypoint | Notes |
| --- | --- | --- |
| Agent runtime | `run_agent.py` | Builds the model loop, tools, memory, and response flow. |
| CLI | `hermes_cli.main:main` via `pyproject.toml` | Dispatches interactive chat and subcommands. |
| Gateway | `gateway/run.py` | Long-lived adapter host for messaging platforms. |
| TUI | `ui-tui` / `tui_gateway` | Node front end with Python backend. |
| Desktop | `apps/desktop/` | Separate chat surface with JSON-RPC transport. |

## Package Hierarchy

### `agent/`
Core logic extracted from the monolithic runtime: memory management, prompt construction, metadata, retries, redaction, tool dispatch helpers, usage accounting, and related support code.

### `tools/`
Self-registering tool modules. Importing the module causes it to call `tools.registry.register(...)`, which feeds the runtime tool schema surface.

### `hermes_cli/`
CLI composition layer: config, setup wizards, plugin discovery, command registry, skills/memory setup, prompt sizing, and shared CLI helpers.

### `gateway/`
Messaging runtime: platform adapters, session tracking, delivery/routing, auth, lifecycle management, and gateway-specific guards.

### `plugins/`
Extension boundary for bundled plugins. This tree includes memory providers, model providers, platform adapters, observability, image generation, and domain-specific plugins.

## Verified Entry Points

### Python console scripts

Defined in [`pyproject.toml`](./pyproject.toml):

- `hermes = hermes_cli.main:main`
- `hermes-agent = run_agent:main`

### Module entrypoints

- `run_agent.py`
- `cli.py`
- `gateway/run.py`
- `batch_runner.py`
- `cron/scheduler.py`

## Dependencies Between Core Layers

```
tools/*.py -> tools.registry -> model_tools.py -> run_agent.py / cli.py / batch_runner.py
plugins/* -> hermes_cli.plugins -> model_tools.py / gateway/* / CLI setup paths
agent/* -> run_agent.py and gateway/* for memory, prompt, tooling, usage
gateway/* -> run_agent.py, hermes_cli.config, hermes_cli.plugins, tools/model layers
```

## Notes

- Hermes is structured as a reusable runtime with behavior added at the edges through tools, plugins, adapters, and CLI subcommands.
- The repository contains both synchronous CLI flows and long-lived daemon-style flows.
- Some platform-specific subtrees are large and load lazily to keep unrelated startup paths cheaper.
