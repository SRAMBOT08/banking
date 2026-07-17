# ServiceNow Architecture Review v2

## 1. Previous Architecture

### Component Flow (Before)
```
Tool Handler (tools.py)
    ↓ Creates MockGateway
    ↓ Calls build_pipeline_runtime(MockGateway())
        ↓ runtime.py:build_pipeline_runtime()
            ↓ Creates ServiceNowClient (per request)
            ↓ Creates TableExecutor
            ↓ Creates PayloadBuilder
            ↓ Creates IncidentService
            ↓ Creates ExecutionVerifier
            ↓ Creates ServiceNowPipeline
    ↓ Calls pipeline.execute_create_incident(request)
    ↓ Calls pipeline.verifier.verify_creation(execution_result)
    ↓ Returns normalized JSON
```

### Problems Identified

1. **MockGateway in Production Code** - The `MockGateway` class was created solely to satisfy the runtime's expectation of a gateway-like object with a `config` attribute. This is an anti-pattern that creates confusion and doesn't follow Hermes' native patterns.

2. **Runtime Created Per Request** - `build_pipeline_runtime()` was called on every tool invocation, creating new HTTP clients, executors, and services each time. This is wasteful and doesn't follow Hermes' singleton pattern for expensive resources.

3. **Tool Handler Over-Orchestration** - The tool handler (`handle_servicenow_create_incident`) was manually calling `execute_create_incident` and `verify_creation` separately, exposing internal pipeline structure that should be encapsulated.

4. **Verification Leaked to Tool Layer** - The tool handler directly invoked `pipeline.verifier.verify_creation()`, violating separation of concerns. The tool should only receive a final result.

5. **No CLI Runtime Binding** - The gateway had `_wire_servicenow_pipeline_runtime()` but CLI mode had no equivalent, meaning the runtime was never bound in CLI sessions.

6. **Dependency Injection Not Following Hermes Standards** - The pattern didn't match how other Hermes plugins (Teams, Spotify) manage long-lived runtimes.

---

## 2. Changes Made

### 2.1 Runtime Module (`plugins/servicenow_pipeline/runtime.py`)

**Added Singleton Pattern:**
- Module-level `_runtime`, `_runtime_error`, `_runtime_config` variables
- Internal `_bind_runtime_internal(config)` method used by both gateway and CLI binders
- `bind_gateway_runtime(gateway)` - binds runtime to gateway instance
- `bind_cli_runtime(config)` - binds runtime for CLI mode using loaded config
- `get_runtime()` - returns singleton runtime or raises if not initialized
- `is_runtime_ready()` - boolean check for availability
- `create_incident(request)` - primary entry point that delegates to `runtime.execute()`

**Removed:**
- `build_pipeline_runtime(gateway)` - no longer creates new runtime per call
- MockGateway dependency eliminated

### 2.2 Tools Module (`plugins/servicenow_pipeline/tools.py`)

**Removed:**
- `MockGateway` class entirely
- Direct `build_pipeline_runtime` import and usage
- Manual orchestration of `execute_create_incident` + `verify_creation`

**Simplified Tool Handler:**
```python
def handle_servicenow_create_incident(args, **kwargs):
    # 1. Validate required fields
    # 2. Build IncidentRequest model
    # 3. Call Runtime.create_incident(request)  <-- Single call
    # 4. Return normalized JSON response
```

**Enhanced `check_servicenow_requirements()`:**
- First checks `is_runtime_ready()` (startup initialization)
- Falls back to env var validation for unit tests/early startup

### 2.3 Pipeline Module (`plugins/servicenow_pipeline/pipeline.py`)

**Enhanced `execute()` method:**
- Propagates `incident_number` and `sys_id` from `ExecutionResult` to `VerificationResult` on success
- Returns complete `VerificationResult` with all identifiers

**Enhanced `VerificationResult` model** (in `models.py`):
- Added optional `incident_number` and `sys_id` fields

### 2.4 CLI Binding (`cli.py`)

**Added ServiceNow CLI runtime binding in `_prepare_deferred_agent_startup()`:**
```python
# Bind ServiceNow pipeline runtime for CLI if plugin is enabled
try:
    from hermes_cli.config import load_config
    from plugins.servicenow_pipeline.runtime import bind_cli_runtime

    config = load_config()
    enabled = config.get("plugins", {}).get("enabled", [])
    if "servicenow_pipeline" in enabled or "servicenow-pipeline" in enabled:
        bind_cli_runtime(config)
except Exception:
    logger.debug("ServiceNow CLI runtime binding skipped", exc_info=True)
```

This runs after plugin discovery and ensures the runtime is ready when the first tool call occurs.

### 2.5 Gateway Binding (Unchanged)

The gateway's `_wire_servicenow_pipeline_runtime()` already called `bind_gateway_runtime(self)` during startup. No changes needed.

---

## 3. Final Architecture

### Component Flow (After)
```
Hermes Startup (Gateway or CLI)
    ↓
Plugin Discovery (discover_plugins())
    ↓
Runtime Binding:
    - Gateway: _wire_servicenow_pipeline_runtime() → bind_gateway_runtime()
    - CLI: _prepare_deferred_agent_startup() → bind_cli_runtime()
    ↓
Singleton Runtime Created Once
    ↓
    ServiceNowPipeline (with IncidentService, TableExecutor, etc.)
    ↓
Tool Invocation
    ↓
Tool Handler (tools.py)
    ↓
    create_incident(IncidentRequest)  ← Single entry point
        ↓
        Runtime.execute()  ← Orchestrates full pipeline + verification
            ↓
            Returns VerificationResult (with incident_number, sys_id)
    ↓
    Normalized JSON Response
```

### Runtime Lifecycle

| Phase | Gateway | CLI |
|-------|---------|-----|
| Plugin Discovery | `discover_plugins()` in gateway startup | `discover_plugins()` in `_prepare_deferred_agent_startup()` |
| Config Load | Gateway config object | `load_config()` from hermes_cli.config |
| Runtime Bind | `bind_gateway_runtime(gateway)` | `bind_cli_runtime(config)` |
| Storage | `gateway._servicenow_pipeline_runtime` | Module singleton `_runtime` |
| Availability | `is_runtime_ready()` / `get_runtime()` | Same module-level functions |

### Dependency Injection Flow

```
Config (YAML + env)
    ↓
bind_*_runtime(config)
    ↓
build_pipeline_runtime_config()  ← Extracts servicenow_pipeline section
    ↓
_build_client_config()  ← Creates ServiceNowClientConfig
    ↓
ServiceNowClient (HTTP session, auth)
    ↓
TableExecutor (CRUD operations)
    ↓
PayloadBuilder (request → payload)
    ↓
IncidentService (orchestrates payload → execute → result)
    ↓
ExecutionVerifier (validates result)
    ↓
ServiceNowPipeline (orchestrates service + verifier)
    ↓
Module Singleton: _runtime = ServiceNowPipeline(...)
```

### Tool Execution Flow

```
LLM Tool Call: servicenow_create_incident({...})
    ↓
Tool Registry → handle_servicenow_create_incident(args)
    ↓
Validate short_description, description
    ↓
IncidentRequest(short_description, description, ...)
    ↓
Runtime.create_incident(request)
    ↓
Runtime.execute(request)  [Full pipeline + verification]
    ↓
VerificationResult(verified=True, message, incident_number, sys_id)
    ↓
tool_result({success, verified, message, incident_number, sys_id})
```

---

## 4. Remaining Technical Debt

1. **Configuration Validation at Bind Time** - The runtime initialization catches exceptions but doesn't validate config schema upfront. Could add explicit validation with descriptive errors.

2. **Runtime Re-binding** - No mechanism to re-bind runtime if config changes (e.g., `hermes config set`). Would require `force=True` parameter or explicit reset function.

3. **Health Check Exposure** - No `health_check()` method exposed on the runtime for monitoring (though `ServiceNowClient.health_check()` exists internally).

4. **Connection Pooling** - `ServiceNowClient` creates a new `requests.Session` per runtime. Could optimize with connection pooling if high throughput needed.

5. **Error Classification** - Tool handler catches all exceptions as generic errors. Could map specific exceptions to user-friendly messages.

6. **Async Support** - Current implementation is synchronous. Future MCP/async tool support would need async variants.

---

## 5. Scalability to Full ServiceNow Platform

This architecture is designed to scale to all ServiceNow domains without structural changes:

| Domain | Implementation Approach |
|--------|------------------------|
| **Incidents** | ✅ Done - `IncidentService`, `IncidentRequest`, `create_incident()` |
| **Change Management** | Add `ChangeRequest`, `ChangeService`, `create_change()` to runtime |
| **Problem Management** | Add `ProblemRequest`, `ProblemService`, `create_problem()` |
| **CMDB** | Add `CiRequest`, `CiService`, `create_ci()`, `query_ci()` |
| **Knowledge** | Add `KnowledgeRequest`, `KnowledgeService`, `search_knowledge()` |
| **Service Catalog** | Add `CatalogRequest`, `CatalogService`, `order_item()` |
| **Asset Management** | Add `AssetRequest`, `AssetService`, `create_asset()` |
| **User/Group** | Add `UserRequest`, `UserService`, `create_user()`, `add_to_group()` |

### Extension Pattern

For each new domain:
1. Add `XxxRequest` and `XxxPayload` models in `models.py`
2. Add `XxxService` in `incidents.py` (or new `xxx.py`) using same `PayloadBuilder` + `TableExecutor` pattern
3. Add `execute_create_xxx()` and `create_xxx()` methods to `ServiceNowPipeline`
4. Add `create_xxx()` to runtime module delegating to pipeline
5. Add tool handler in `tools.py` calling `runtime.create_xxx()`
6. Register tool in `__init__.py` with new schema

**No changes needed to:**
- Runtime singleton lifecycle
- Gateway/CLI binding
- Pipeline orchestration pattern
- Verification integration
- Tool registration mechanism

---

## 6. Why This Architecture Is Suitable

### Follows Hermes Native Patterns
- **Singleton Runtime**: Matches Teams pipeline, Spotify client, memory providers
- **Startup Binding**: Gateway binds in `_wire_*`, CLI binds in deferred startup
- **Plugin Registration**: Uses standard `ctx.register_tool()` with `check_fn`
- **Config-Driven**: Reads from `config.yaml` + env vars, no hardcoded paths

### Separation of Concerns
| Layer | Responsibility |
|-------|----------------|
| Tool Handler | Input validation, model building, response formatting |
| Runtime | Singleton lifecycle, config → dependency wiring |
| Pipeline | Orchestration, error handling, verification integration |
| Service | Business logic, payload prep, executor delegation |
| Executor | Generic CRUD for any ServiceNow table |
| Client | HTTP transport, auth, retries, error normalization |
| Verifier | Success criteria, rule validation |

### Testability
- Each layer independently testable with mocks
- Singleton runtime can be reset in tests via `_runtime = None`
- Tool handler tests mock `get_runtime()` not internal pipeline methods
- Integration tests verify full flow Planner → Registry → Handler → Runtime → Pipeline

### Maintainability
- Single entry point per domain operation (`create_incident`, `create_change`, etc.)
- Pipeline owns all orchestration - tool handler stays thin
- Verification encapsulated in pipeline, not leaked to tool layer
- Adding new domains follows consistent pattern

---

## 7. Migration Checklist

- [x] Remove `MockGateway` from production code
- [x] Implement singleton runtime with `bind_gateway_runtime()` / `bind_cli_runtime()`
- [x] Add `create_incident()` as single tool entry point
- [x] Move verification into pipeline `execute()` method
- [x] Propagate `incident_number`/`sys_id` through `VerificationResult`
- [x] Add CLI runtime binding in `_prepare_deferred_agent_startup()`
- [x] Update unit tests to mock `get_runtime()` instead of `build_pipeline_runtime()`
- [x] Add integration tests covering Planner → Registry → Handler → Runtime → Pipeline
- [x] Document architecture in this review

---

## 8. Conclusion

The refactored ServiceNow plugin now follows Hermes' established architectural patterns:

1. **Long-lived singleton runtime** created once at startup (gateway or CLI)
2. **Thin tool handlers** that delegate to `Runtime.create_incident()`
3. **Encapsulated orchestration** in `ServiceNowPipeline.execute()`
4. **Standard plugin registration** via `ctx.register_tool()`
5. **Config-driven** with proper fallback for unit tests

This architecture is the **official implementation standard** for all future ServiceNow capabilities. New domains (Change, Problem, CMDB, Knowledge, Catalog, Assets, Users) should extend this pattern by adding domain-specific services and runtime methods without modifying the core lifecycle management.