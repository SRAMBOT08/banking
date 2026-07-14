Ingestion Service Contract

Responsibility:
- Consume external telemetry, validate schemas, deduplicate events, normalize to Unified Event Model and publish to internal topics.

Inputs:
- External telemetry streams (brokered)

Outputs:
- Unified Event Model messages to Kafka

Kafka Topics Produced:
- events.unified.v1

Kafka Topics Consumed:
- external.telemetry.* (ingestion adapters)

Database Ownership:
- none (stateless processing; may persist offsets)

External Integrations:
- External telemetry feeds (placeholder)

Dependencies:
- shared library

Shared Models Used:
- shared.models.events.UnifiedEvent
