# Class Diagram

## Major Classes Observed

| Class | File | Responsibility |
| --- | --- | --- |
| `AIAgent` | `run_agent.py` | Main runtime agent orchestration. |
| `ToolRegistry` | `tools/registry.py` | Central tool metadata and handler registry. |
| `ToolEntry` | `tools/registry.py` | Tool metadata record. |
| `MemoryProvider` | `agent/memory_provider.py` | Abstract memory provider contract. |
| `MemoryManager` | `agent/memory_manager.py` | Memory provider orchestration. |
| `SessionSource` | `gateway/session.py` | Gateway session origin and routing metadata. |
| `PlatformRegistry` | `gateway/platform_registry.py` | Platform adapter registry. |
| `PlatformEntry` | `gateway/platform_registry.py` | Platform adapter metadata/factory. |

## Relationships

- `AIAgent` consumes `MemoryManager`, `model_tools`, and tool registry state.
- `MemoryManager` consumes one or more `MemoryProvider` implementations.
- `PlatformRegistry` stores `PlatformEntry` instances and creates adapters.
- Tool files depend on `tools.registry` and register themselves at import time.

## Unable to Verify

A full UML-style class diagram would require tracing every class in the repository, which was not completed here.

> Unable to verify from the current codebase.
