# Event Schema Specification

## Purpose
This document specifies the event-driven schemas, Kafka topic configurations, retry strategies, and message payloads running in the Lokii Platform.

## Overview
Lokii utilizes Apache Kafka as its central messaging backbone. Services communicate asynchronously by publishing structured events to Kafka topics, ensuring decoupling, scalability, and event replay capabilities. Every topic is mapped to a single producing service owner to enforce governance boundaries.

---

## Detailed Explanation

### 1. Topic Registry
The platform registers and scopes the following Kafka topics:

| Topic Name | Producer Service | Consumer Service(s) | Purpose |
|------------|------------------|---------------------|---------|
| `events.unified.v1` | Ingestion Service | Evidence Service, Investigation Service | Unified telemetry events (authentication, transaction) |
| `events.unified.dlq.v1` | Ingestion Service | Operations tool / Archiver | Ingest failure dead letter queue |
| `evidence.graph.events.v1` | Evidence Service | Threat Intelligence, AI Service | Graph update events |
| `investigation.candidates.v1` | Threat Intelligence | Investigation Service | Identified threat alerts requiring triage |
| `investigations.updated.v1` | Investigation Service | AI Service, Execution Service, Frontend | Broadcasts active status changes |
| `investigation.completed.v1` | Investigation Service | Case Builder, Execution Service | Concluded investigation summaries |
| `case.created.v1` | Case Builder | AI Report Service, Execution Service | Published CaseFile records |
| `report.generated.v1` | AI Report Service | Execution Service | Completed incident reports |
| `execution.ready.v1` | Execution Service | ServiceNow Adapter | Approved containment tasks |

### 2. Global Retry and DLQ Strategy
- **Retry Policy**: Consumers implement 3 retry attempts with exponential backoff (e.g. base delay 1s, backoff factor 2) when processing fails.
- **Dead Letter Queue**: If retries exceed the limit, the event is written to a topic-specific DLQ (e.g., `events.unified.dlq.v1` for telemetry ingestion failures).
- **Reprocessing**: Messages in a DLQ are stored for 7 days, allowing administrators to inspect payloads, address errors, and trigger reprocessing.

### 3. Correlation and Tracing
Every event extends a `BaseEvent` model containing metadata to trace transactions across services:
- `event_id` (UUID): Unique event identifier.
- `correlation_id` (UUID): Links all events triggered by a single transaction or scenario.
- `trace_id` (UUID): Internal trace identifier for log correlation.
- `tenant_id` (str): Tenant partition identifier.
- `timestamp` (str): Origin timestamp.

---

## Workflow

### Lifecycle of a Telemetry Event
1. **Emit**: Event Simulator posts raw telemetry.
2. **Normalize**: Ingestion Service parses, validates, adds deduplication keys, and writes to `events.unified.v1`.
3. **Trace**: Downstream services (Evidence, Threat, Investigation) consume the event, preserving the `correlation_id` and `trace_id` in subsequent messages.
4. **Log**: Execution services log status changes to Kafka topics, ensuring end-to-end trace tracking.

---

## Design Decisions
- **Single-Producer Enforcement**: To maintain data integrity, each Kafka topic has a single producing service owner.
- **Deduplication Keys**: Telemetry events require deduplication keys (such as `event_id`) to prevent duplicate processing.

## Best Practices
- **Schema Validation**: Validate event bodies against Pydantic models before publishing to Kafka.
- **Idempotent Consumers**: Ensure event consumers are idempotent to handle message replays safely.

## Future Enhancements
- Set up a Schema Registry (such as Confluent Schema Registry) to manage and version event schemas.
- Implement partition keys based on `tenant_id` or `correlation_id` to maintain strict event ordering.
