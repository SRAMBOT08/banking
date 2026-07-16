# Extension Points

## Verified Extension Points

### Tool Registry

Tools self-register through `tools.registry`.

### Plugin System

Plugins can register hooks, CLI commands, tools, and adapters through `hermes_cli.plugins`.

### Memory Providers

`MemoryProvider` is an abstract interface for pluggable memory backends.

### Platform Registry

`gateway.platform_registry` allows adapters to be created from registry entries rather than hardcoded switches.

### CLI Command Registry

The CLI command system is centralized and extensible through shared command definitions and handlers.

### Scheduler

The cron subsystem provides job lifecycle and background execution entrypoints.

## Notable Hook Surfaces

- plugin lifecycle hooks
- tool availability checks
- pre/post LLM hooks
- gateway dispatch hooks
- session lifecycle hooks
- memory-provider hooks

## Unable to Verify

This document only lists extension points that were visible in the reviewed source.

> Unable to verify from the current codebase.
