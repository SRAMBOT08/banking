# Architecture Summary

## Verified Summary

Hermes is a reusable AI agent runtime with four major axes:

1. Agent conversation/runtime execution
2. Tool discovery and dispatch
3. Memory-provider integration
4. Gateway/plugin extension surfaces

## Major Design Patterns

- registry-driven tool loading
- plugin-based extension
- provider abstraction for memory
- deferred platform loading
- long-lived gateway/session state
- prompt assembly as a distinct subsystem

## Major Layers

- bootstrap
- CLI entrypoints
- agent runtime
- tool framework
- plugin loader
- gateway
- scheduler
- shared desktop/TUI transport

## Verified Conclusions

- Hermes is built as a general runtime, not a fixed domain app.
- Extension belongs at the edges through plugins, adapters, tools, and providers.
- The repository already contains the subsystem boundaries needed to document it as a platform.

## Unable to Verify

This summary intentionally avoids claims that were not directly confirmed in source.

> Unable to verify from the current codebase.
