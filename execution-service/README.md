# Execution Decision & Orchestration Service

Phase 8 introduces SentinelIQ's deterministic Execution Decision & Orchestration Platform.

## Purpose

This service decides **what** governed execution should happen after a completed investigation.
It does not implement connectors and does not execute enterprise actions directly.

## Deterministic responsibilities

- Consume completed investigation payloads from `investigation.completed.v1`
- Build deterministic execution plans from snapshot-derived recommendations
- Evaluate pluggable policies (risk, tenant, compliance/scheduling boundaries)
- Determine approval workflows and expiration
- Manage deterministic dependency-aware task queues
- Drive task lifecycle state machine
- Verify expected vs observed results
- Generate immutable audit records
- Publish execution lifecycle Kafka events

## Out of scope

- ServiceNow/Jira/Slack/Okta integrations
- Browser automation / SOAR connectors
- Any direct enterprise-system action execution
- Any AI/LLM reasoning

## API

- GET `/execution/plans`
- GET `/execution/tasks`
- GET `/execution/status`
- GET `/execution/audit`
- GET `/execution/history`
- GET `/execution/metrics`
- POST `/execution/plans`
- POST `/execution/approve`
- POST `/execution/cancel`
- POST `/execution/retry`
- POST `/execution/replay`
- PATCH `/execution/tasks/{id}`

## Runtime

- Service port: `8700`
- Deterministic in-memory execution repository
- Kafka contracts documented in `docs/Kafka Contracts.md`
