# SentinelIQ Integration Harness

This is a repository-level integration test harness, not a microservice. It exercises the existing service boundary contracts in-process with deterministic Kafka-shaped messages and a mock ServiceNow adapter.

## One-command run

From the repository root:

`python -m integration.run`

## Automated tests

`python -m pytest -q tests/test_end_to_end_integration.py`

The five scenarios are Credential Stuffing, Account Takeover, Money Mule, Insider Threat, and Ransomware. Each run preserves correlation ID, investigation ID, case ID, report ID, execution ID, and a Kafka message ID across the stage metrics.

## Why in-process

The current Compose topology does not yet provide every live link: knowledge-service is a placeholder container, evidence does not publish its graph topic, investigation does not publish the execution completion topic, and Case Builder/AI Report callers are not wired. See `docs/contract_validation_report.md` for the live topology gaps.
