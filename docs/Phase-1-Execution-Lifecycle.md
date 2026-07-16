# Phase 1 Execution Lifecycle

This document traces one complete runtime path from a user request to a produced response in Hermes.

Scope:

- Runtime execution only
- CLI-first conversational path
- No UI, desktop, web, documentation, tests, packaging, assets, or localization details

## Execution Path Summary

```text
User request
→ cli.py:main()
→ HermesCLI.__init__()
→ hermes_cli.config.load_config()
→ model_tools.discover_builtin_tools()
→ hermes_cli.plugins.discover_plugins()
→ HermesCLI.chat() / HermesCLI.run()
→ run_agent.AIAgent.__init__()
→ model_tools.get_tool_definitions()
→ run_agent.AIAgent.run_conversation()
→ model_tools.handle_function_call()
→ tool handler / business logic
→ hermes_state.SessionDB
→ final assistant response returned
```

## 1. Entry Point

| File | Function | Responsibility | Next Component |
|---|---|---|---|
| `cli.py` | `main()` | Receives the user-facing request path for the interactive CLI and selects the runtime mode, including single-turn or interactive conversation handling. | `HermesCLI` initialization |
| `run_agent.py` | `main()` | Alternate direct-agent entrypoint for non-CLI invocation paths. | `AIAgent` initialization |
| `gateway/run.py` | `main()` | Messaging gateway entrypoint for non-CLI channels. Not used in the CLI request trace, but it is the equivalent runtime entrypoint for platform delivery. | `GatewayRunner` initialization |

## 2. Runtime Initialization

| File | Function | Responsibility | Next Component |
|---|---|---|---|
| `cli.py` | `HermesCLI.__init__()` | Builds the interactive CLI runtime, prepares display behavior, session state, tool settings, and agent-facing options. | Configuration loading and session setup |
| `run_agent.py` | `AIAgent.__init__()` | Builds the agent runtime, resolves model/provider state, and prepares the conversation engine. | Tool schema discovery and conversation setup |
| `gateway/run.py` | `GatewayRunner.__init__()` | Builds gateway runtime state for platform session management and delivery orchestration. | Gateway configuration and adapter setup |

## 3. Configuration Loading

| File | Function | Responsibility | Next Component |
|---|---|---|---|
| `hermes_cli/config.py` | `load_config()` | Loads the active Hermes configuration from the profile-aware config location and returns the merged runtime configuration used by the CLI and agent. | Runtime initialization and downstream feature selection |
| `run_agent.py` | module-level startup path invoking `load_hermes_dotenv()` | Loads environment variables before the agent runtime proceeds so API keys and local overrides are available. | Agent initialization and provider setup |
| `cli.py` | `load_cli_config()` | Loads CLI-facing configuration and normalizes runtime options used by the interactive loop. | `HermesCLI.__init__()` |
| `gateway/run.py` | `cfg_get()` / `load_config()` call sites | Reads runtime settings for gateway behavior, platform enablement, and delivery policies. | Gateway runner initialization |

## 4. Plugin Discovery

| File | Function | Responsibility | Next Component |
|---|---|---|---|
| `model_tools.py` | `discover_builtin_tools()` | Imports built-in tool modules so each tool can self-register before the agent asks for a tool schema. | Tool registry population |
| `model_tools.py` | `discover_plugins()` | Loads plugin-provided tools and capabilities into the process-level registry. | Tool registry population |
| `gateway/run.py` | plugin discovery startup path | Performs gateway-side plugin discovery before runtime dispatch so platform sessions can see plugin capability. | Gateway tool/runtime assembly |

## 5. Pipeline Creation

| File | Function | Responsibility | Next Component |
|---|---|---|---|
| `cli.py` | `HermesCLI.chat()` | Creates the request pipeline for a user message by preparing input, session context, and agent invocation state. | Agent execution |
| `cli.py` | `HermesCLI.run()` | Drives the interactive loop and repeatedly hands submitted user requests into the agent pipeline. | Agent execution |
| `run_agent.py` | `AIAgent.run_conversation()` | Constructs the conversation pipeline and manages the turn-by-turn model/tool loop. | Model request dispatch |
| `model_tools.py` | `get_tool_definitions()` | Builds the tool schema list that is attached to the model request for the active session. | Model API call / response loop |

## 6. Request Processing

| File | Function | Responsibility | Next Component |
|---|---|---|---|
| `run_agent.py` | `AIAgent.run_conversation()` | Owns the main agent loop that sends the request to the model, receives tool calls, and repeats until a final answer is produced. | Tool-call handling or final response return |
| `run_agent.py` | `AIAgent.chat()` | Thin wrapper around the conversation loop for single-message execution. | `AIAgent.run_conversation()` |
| `model_tools.py` | `handle_function_call()` | Receives a requested tool/function name from the model and routes it to the correct tool implementation. | Tool execution backend |
| `gateway/run.py` | request/turn handling path | Converts platform input into a session turn and forwards it into the agent runtime. | `AIAgent` conversation loop |

## 7. Tool Execution

| File | Function | Responsibility | Next Component |
|---|---|---|---|
| `model_tools.py` | `handle_function_call()` | Dispatches a requested tool call to the registry and applies tool scoping rules. | Tool registry entry |
| `tools/registry.py` | `ToolRegistry.register()` / registry dispatch path | Stores tool metadata, schema, handler, and availability information. | Concrete tool handler |
| `tools/registry.py` | `discover_builtin_tools()` | Imports tool modules that self-register their handlers and schemas. | Individual tool modules |
| `tools/terminal_tool.py` | terminal tool entrypoints | Executes shell commands or environment-backed actions when the model requests terminal execution. | Underlying runtime environment backend |
| `tools/browser_*`, `tools/file_*`, `tools/vision_*`, `tools/memory_*`, `tools/mcp_*` | tool handlers | Execute their specific tool responsibilities against external systems or local state. | Business logic / persistence / external service |

## 8. Business Logic Execution

| File | Function | Responsibility | Next Component |
|---|---|---|---|
| `agent/` modules | provider, memory, prompt, compression, and routing helpers | Perform the core agent business logic around prompting, memory, context shaping, and model/provider behavior. | Response assembly and state updates |
| `agent/context_compressor.py` | context compression flow | Reduces conversation history when the runtime decides the context should be compacted. | Session/state persistence and continued conversation |
| `agent/prompt_builder.py` | prompt composition helpers | Assembles system and runtime prompts used for the model request. | Model request execution |
| `agent/memory_manager.py` | memory sanitization and memory coordination | Coordinates memory-related business rules before or after turn processing. | Persistence and memory provider updates |

## 9. State Persistence

| File | Function | Responsibility | Next Component |
|---|---|---|---|
| `hermes_state.py` | `SessionDB.__init__()` | Opens and initializes the session store used for conversation history and runtime state. | Session read/write operations |
| `run_agent.py` | `_flush_messages_to_session_db()` | Persists conversation messages into the session database during and after a turn. | `hermes_state.SessionDB` |
| `run_agent.py` | `_save_trajectory()` | Stores trajectory data for later analysis or replay when enabled. | Trajectory storage path |
| `gateway/run.py` | `AsyncSessionDB(SessionDB())` usage | Persists gateway-side session state and delivery lifecycle data for multi-platform conversations. | SQLite-backed session storage |
| `hermes_state.py` | session write helpers and schema management | Maintains durable transcript and search state. | Stored session history and search indexing |

## 10. Response Generation

| File | Function | Responsibility | Next Component |
|---|---|---|---|
| `run_agent.py` | `AIAgent.run_conversation()` | Produces the final assistant response once tool calls are complete or the model returns a terminal answer. | Caller-facing return value |
| `run_agent.py` | `AIAgent.chat()` | Returns the final response string to the CLI or other caller. | CLI output rendering |
| `cli.py` | `HermesCLI.chat()` | Converts the model output into terminal-visible response handling. | Terminal display / session continuation |
| `gateway/run.py` | gateway response delivery path | Sends the final response back to the originating platform session. | Platform adapter delivery |

## Complete Lifecycle Trace

| Step | File | Function | Responsibility | Next Component |
|---|---|---|---|---|
| 1 | `cli.py` | `main()` | Starts the CLI request path. | `HermesCLI.__init__()` |
| 2 | `cli.py` | `HermesCLI.__init__()` | Initializes runtime state. | `load_config()` |
| 3 | `hermes_cli/config.py` | `load_config()` | Loads runtime configuration. | CLI and agent setup |
| 4 | `model_tools.py` | `discover_builtin_tools()` | Imports built-in tools for registration. | `tools/registry.py` |
| 5 | `model_tools.py` | `discover_plugins()` | Loads plugin capabilities into the registry. | Tool registry population |
| 6 | `cli.py` | `HermesCLI.chat()` | Begins request processing for the user message. | `AIAgent.run_conversation()` |
| 7 | `run_agent.py` | `AIAgent.__init__()` | Creates the agent runtime. | Tool schema build |
| 8 | `model_tools.py` | `get_tool_definitions()` | Creates the active tool schema set. | Model request assembly |
| 9 | `run_agent.py` | `AIAgent.run_conversation()` | Runs the model/tool loop. | `handle_function_call()` or final answer |
| 10 | `model_tools.py` | `handle_function_call()` | Dispatches tool calls. | Concrete tool handler |
| 11 | `tools/*` | tool handler entrypoint | Executes business logic or external action. | State update / persistence |
| 12 | `run_agent.py` | `_flush_messages_to_session_db()` | Persists the turn and conversation state. | `hermes_state.SessionDB` |
| 13 | `run_agent.py` | `AIAgent.run_conversation()` | Returns the final response. | `AIAgent.chat()` / CLI |
| 14 | `cli.py` | `HermesCLI.chat()` | Emits the response to the terminal. | User |

## Notes on the Trace

- The trace above follows the CLI conversational path because that is the canonical user request path in Hermes.
- The same agent core is reused by gateway and other runtime surfaces, but those are separate entry paths.
- Tool discovery is process-wide and happens before the model request loop begins so the request can be assembled with the active tool schema set.

