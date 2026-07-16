# SentinelIQ Platform Integration Report

## Scope

This phase adds a deterministic in-process integration harness; it does not add a microservice or new domain capability. The harness uses Kafka-shaped payload boundaries and the existing simulator contract, then validates the downstream CaseFile, report, execution, and ServiceNow adapter artifacts with a mock adapter response.

## Validated workflow

1. Enterprise event simulator generates realistic deterministic telemetry.
2. Ingestion validates, normalizes, deduplicates, and routes records.
3. Evidence derives entities and relationships.
4. Threat intelligence correlates scenario evidence.
5. Knowledge enriches controls and patterns.
6. Graph stores the deterministic entity relationship view.
7. Memory returns historical context.
8. Aggregator packages evidence, threat, knowledge, graph, history, timeline, and provenance.
9. Investigation agent output is represented as the completed workflow result.
10. Case Builder artifact is immutable-shaped, versioned, audited, and provenance-linked.
11. AI Report artifact is traceable to the CaseFile.
12. Execution artifact is policy-approved and contains a connector action.
13. ServiceNow adapter mock creates the incident result.

## Scenarios

- Credential Stuffing
- Account Takeover
- Money Mule
- Insider Threat
- Ransomware

## Run

From the repository root:

`python -m integration.run`

The automated test is `tests/test_end_to_end_integration.py`.

## Important boundary

This is an in-process contract integration test, not a claim that the current Docker Kafka topology is fully connected. The contract validation report documents the remaining live-topology gaps.
