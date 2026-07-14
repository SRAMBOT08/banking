SentinelIQ shared library

This package provides versioned, reusable artifacts for all services.

Structure:
- common: general helpers
- config: typed settings and configuration helpers
- constants: central constants
- enums: common enums
- events: unified event model and contract references (docs-only)
- kafka: topic registry and producer/consumer interfaces (stubs only)
- logging: structured logging helpers and guidance
- middleware: cross-service middleware (correlation id, request tracing placeholders)
- models: shared Pydantic models (contracts only)
- schemas: JSON Schema and contract exports
- security: auth-related models and secrets guidance (placeholders)
- exceptions: base exceptions and mapping to HTTP
- utils: small helper utilities

Notes:
- This package contains only placeholders and documentation in Phase 1. No business logic.
- Versioning: semantic versioning enforced. Breaking changes require major version bump.
