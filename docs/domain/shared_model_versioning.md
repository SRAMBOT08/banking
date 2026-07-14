# Shared Model Versioning Strategy

Purpose
- Define how `shared/` models evolve without breaking consumers.

Principles
- Semantic versioning for the shared package (MAJOR.MINOR.PATCH).
- Backward-compatible changes increment MINOR/PATCH; breaking changes increment MAJOR.
- Consumers must declare compatible shared-model major versions in their service manifests.

Process
- All changes to shared models require a CHANGELOG entry and an ADR if they are breaking.
- Consumer-driven contract tests: changes that affect message or model shape must add contract tests in the shared repo and CI. Consumers must run the shared contract tests before upgrading major versions.
- Deprecation window: fields deprecated must remain for at least two release cycles (configurable by org) before removal.

Schema Storage
- Canonical JSON Schemas for message types are stored under `docs/contracts/` and `shared/schemas/` and must reference the shared-model semantic version.

Ownership
- `shared/` is owned by Platform with contributions gated by ADR and code review.
