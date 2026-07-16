# Gateway Architecture

## Overview

The gateway is the long-lived process that hosts messaging platform adapters, routes inbound messages, and binds them to agent sessions.

## Primary Files

- [`gateway/run.py`](./gateway/run.py)
- [`gateway/session.py`](./gateway/session.py)
- [`gateway/platform_registry.py`](./gateway/platform_registry.py)
- `gateway/platforms/`

## Responsibilities

- initialize configured adapters
- route inbound messages to sessions
- manage session metadata and persistence
- coordinate auth and platform-specific delivery
- handle platform-specific lifecycle concerns

## Session Handling

`gateway/session.py` models the source of a message and the routing context used for delivery.

It includes:

- platform
- chat identity
- user identity
- thread metadata
- profile scope
- relay trust markers

## Platform Registry

`gateway/platform_registry.py` provides a registry for platform adapters.

It supports:

- deferred loader registration
- adapter factories
- config validation
- setup hooks
- standalone senders
- plugin ownership metadata

## Verified Characteristics

- The gateway is a host process, not the agent loop itself.
- Adapter creation can be deferred until a platform is actually needed.
- The registry is intended to support both built-in and plugin-defined adapters.
