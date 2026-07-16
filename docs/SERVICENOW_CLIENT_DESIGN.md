# ServiceNow Client Design

## Purpose

The ServiceNow client is the single reusable transport boundary for future
ServiceNow capability modules. It exists so higher-level modules can issue
requests without knowing anything about HTTP session management, headers,
timeouts, or response normalization.

## Responsibilities

- manage instance URL configuration
- validate and normalize authentication settings
- own HTTP session lifecycle
- build default headers
- execute generic requests
- normalize responses
- convert transport failures into reusable Hermes exceptions
- expose a local health/readiness view

## Public API

| Method | Purpose |
|---|---|
| `__init__()` | Bind client configuration and optional logger/session factory |
| `authenticate()` | Validate local auth configuration and initialize session state |
| `build_headers()` | Assemble default and extra request headers |
| `request()` | Execute a generic request against the ServiceNow instance |
| `close()` | Close the underlying session |
| `health_check()` | Return local readiness information without network access |

## Configuration

| Field | Purpose |
|---|---|
| `instance_url` | Base URL for the ServiceNow instance |
| `authentication_type` | Auth mode selector such as `basic` or `bearer` |
| `username` | Username for basic auth |
| `password` | Password for basic auth |
| `access_token` | Token for bearer-style auth |
| `timeout` | Default request timeout in seconds |
| `verify_ssl` | TLS verification toggle |
| `retry_policy` | Declarative retry settings for future orchestration layers |

## Exception Hierarchy

| Exception | Meaning |
|---|---|
| `ServiceNowError` | Base class for all client errors |
| `AuthenticationError` | Authentication configuration is invalid or incomplete |
| `RequestError` | Request cannot be prepared or response is invalid |
| `ConnectionError` | Underlying HTTP transport failed |

## Future Extension Points

- higher-level capability modules can call `client.request(...)` without
  knowing the HTTP implementation
- retry orchestration can be layered on top using `retry_policy`
- future auth strategies can be added without changing request callers
- response parsing can be specialized outside the client
- health/readiness checks can be used by runtime or CLI surfaces

## Design Decisions

- The client is generic and domain-agnostic.
- It does not know about incidents, changes, CMDB, knowledge, or catalog.
- It uses typed configuration objects so future modules have a stable contract.
- It keeps network behavior isolated behind one reusable entry point.
- It avoids eager network calls and only validates local configuration in
  `health_check()` and `authenticate()`.

