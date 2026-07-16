# Execution Engine

## Scope

In Hermes, the execution engine is the agent runtime path that runs model turns, dispatches tools, and handles retries, timeouts, and turn lifecycle.

## Primary Files

- [`run_agent.py`](./run_agent.py)
- `agent/async_utils.py`
- `agent/retry_utils.py`
- `agent/tool_dispatch_helpers.py`

## Responsibilities

- manage the conversation loop
- call the model
- inspect tool calls
- run tool handlers
- normalize outputs
- handle retry/error paths
- preserve durable session state

## Observed Behavior

- Async tool calls are bridged through persistent event loops.
- Tool execution can happen in worker threads.
- The runtime protects against closed-loop cleanup issues by keeping loops alive for the lifetime of the calling thread.

## Unable to Verify

The reviewed code does not expose a single class literally named `ExecutionEngine`.

> Unable to verify from the current codebase.
