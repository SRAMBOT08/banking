# Runtime Architecture

This document describes the current runtime layers that are visible from the source tree.

## Core Runtime Layers

| Subsystem | Responsibility | Primary files |
| --- | --- | --- |
| Agent runtime | Conversation loop, tool calling, model client orchestration | `run_agent.py`, `agent/*` |
| Tool framework | Tool discovery, registry, availability checks, dispatch | `tools/registry.py`, `model_tools.py` |
| Memory | Provider abstraction, memory prompt injection, prefetch/sync | `agent/memory_provider.py`, `agent/memory_manager.py` |
| Gateway | Messaging adapter host and session routing | `gateway/run.py`, `gateway/session.py`, `gateway/platform_registry.py` |
| CLI | Interactive operator surface and setup flows | `cli.py`, `hermes_cli/*` |
| Plugins | Bundled extension boundary | `plugins/*`, `hermes_cli/plugins.py` |
| Scheduler | Cron/background job lifecycle | `cron/*` |

## Agent Runtime

The agent runtime in `run_agent.py` is the central conversational engine. It:

- loads environment/config state
- assembles prompt and model inputs
- resolves tool definitions
- executes model calls
- handles tool calls
- manages memory sync and prompt injection
- persists session-visible state

## Tool Framework

The tool system is registry-driven.

- Tool modules self-register through `tools.registry`.
- `model_tools.py` imports/discovers tools and exposes tool metadata to the agent.
- Tool availability is gated by registry checks and toolset resolution.

## Memory

The memory layer is provider-based.

- `agent.memory_provider.MemoryProvider` defines the provider contract.
- `agent.memory_manager.MemoryManager` is the runtime integration point.
- Providers may add prompt blocks, prefetch context, sync completed turns, and expose tools.

## Gateway

The gateway runs as a long-lived process for message platforms.

- session routing and origin tracking live in `gateway/session.py`
- platform registry and adapter creation live in `gateway/platform_registry.py`
- platform-specific code lives under `gateway/platforms/`

## Plugin Model

Plugins are first-class extension units. They can contribute:

- CLI commands
- runtime hooks
- tools
- platform adapters
- plugin-local state or orchestration

## Verified Boundaries

- Core runtime code remains generic and reusable.
- Domain-specific behavior is placed in tools, plugins, or platform modules.
- The codebase uses explicit registries instead of import-time global branching.
