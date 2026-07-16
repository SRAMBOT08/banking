# Tool Framework

## Core Files

- [`tools/registry.py`](./tools/registry.py)
- [`model_tools.py`](./model_tools.py)
- tool modules under `tools/`

## Tool Registration

Tool modules self-register by calling `registry.register(...)` at module import time.

The registry stores:

- tool name
- toolset membership
- schema
- handler
- availability check
- description
- async/sync metadata

## Discovery

`discover_builtin_tools()` scans `tools/*.py`, imports modules that contain top-level `registry.register(...)` calls, and returns the imported module list.

`model_tools.py` then imports plugin discovery and constructs the runtime-facing tool definition surface.

## Availability Checks

Toolset availability can be gated by `check_fn`.

The registry caches check results and keeps recent-good results available for a short grace period to avoid transient flake from removing tools mid-session.

## Execution

`handle_function_call(...)` is the main dispatch entrypoint used by the agent loop.

The tool framework also manages:

- async bridging
- result normalization
- toolset-to-tool mapping
- tool availability reporting

## Verified Characteristics

- The tool framework is registry-first, not hardcoded.
- Tool discovery runs at startup through module import side effects.
- Tool schemas are the model-facing contract.
