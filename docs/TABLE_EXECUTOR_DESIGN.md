# Table Executor Design

## Purpose

The table executor is the generic CRUD layer for ServiceNow tables. It exists
to let future capability modules perform record operations without knowing
transport details.

## Responsibilities

- accept a ServiceNow client through dependency injection
- normalize table and record identifiers
- call the generic client request API
- wrap responses in typed executor result objects
- convert client transport exceptions into executor-level exceptions
- keep table semantics generic

## Supported Operations

| Operation | Purpose |
|---|---|
| `create_record()` | Create a new record in any ServiceNow table |
| `get_record()` | Retrieve a record by identifier |
| `update_record()` | Update a record by identifier |
| `delete_record()` | Delete a record by identifier |
| `query_records()` | Query records using a ServiceNow query string |

## Dependency Diagram

```text
Future capability modules
        ↓
TableExecutor
        ↓
ServiceNowClient
        ↓
HTTP transport
```

## Class Diagram

```text
ServiceNowClient
    ↑
    |
TableExecutor
    ├── TableRecord
    ├── TableQueryResult
    └── TableDeleteResult
```

## Execution Flow

```text
caller
  ↓
TableExecutor.create/get/update/delete/query
  ↓
ServiceNowClient.request(...)
  ↓
normalized response
  ↓
typed executor result
```

## Future Extension Points

- future modules can add higher-level workflows on top of the executor
- additional result wrappers can be introduced without changing client transport
- retry orchestration can be layered above the executor
- table-specific validation can be added outside the executor
- response enrichment can be added outside the executor

## Design Decisions

- No hardcoded table names
- No business rules
- No payload mapping
- No HTTP implementation details exposed to callers
- Typed wrappers are used where practical instead of raw dictionaries

