# Memory Architecture

## Purpose

Memory in Hermes is a provider-driven persistence and recall layer.

## Primary Files

- [`agent/memory_provider.py`](./agent/memory_provider.py)
- [`agent/memory_manager.py`](./agent/memory_manager.py)
- `hermes_cli/memory_setup.py`

## Memory Provider Contract

`MemoryProvider` defines the lifecycle:

- `is_available()`
- `initialize(session_id, **kwargs)`
- `system_prompt_block()`
- `prefetch(query, session_id=...)`
- `sync_turn(user_content, assistant_content, session_id=..., messages=...)`
- `get_tool_schemas()`
- `handle_tool_call(...)`
- `shutdown()`

It also defines optional hooks for session switches, compression, delegation, and setup integration.

## Memory Manager

`MemoryManager` is the single integration point used by the agent runtime.

It is responsible for:

- selecting and managing providers
- building memory prompt blocks
- prefetching recall context
- syncing completed turns
- queuing background recall
- injecting provider tools into the tool surface

## Verified Constraints

- Only one external provider is allowed at a time.
- Providers can contribute both prompt text and tools.
- The manager is responsible for normalizing provider tool schemas so malformed tool metadata does not poison the request.
