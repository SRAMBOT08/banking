# Node RPC Analysis

## Verified Components

The repository contains a Node/TypeScript transport layer used by desktop and shared clients:

- `apps/shared/src/json-rpc-gateway.ts`
- `apps/shared/src/websocket-url.ts`
- `apps/desktop/`
- `ui-tui/`

## Observed Architecture

- Shared code defines WebSocket and JSON-RPC client primitives.
- The desktop client uses these primitives to talk to a Python backend.
- The TUI uses stdio JSON-RPC between Ink and the Python gateway.

## Communication Model

The reviewed source confirms:

- request/response messaging over JSON-RPC
- WebSocket transport for browser/desktop surfaces
- stdio transport for the TUI

## Unable to Verify

A complete method-by-method RPC catalog was not fully traced in the time available.

> Unable to verify from the current codebase.
