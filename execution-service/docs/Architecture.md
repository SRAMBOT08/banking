# Execution Decision & Orchestration Platform Architecture

The Execution Decision & Orchestration Platform is a deterministic post-investigation service.

## Position in platform

`Investigation Service -> AI Service -> Execution Service -> (Future) Connector Framework`

## Deterministic boundaries

- Input boundary: `investigation.completed.v1` only.
- No raw event consumption.
- No connector implementation.
- No AI/LLM dependencies.

## Layers

- **Domain**: typed models, state machine, deterministic ordering.
- **Application**: planner, policy engine, approval engine, queue engine, orchestrator, verification, audit.
- **Interface**: REST and Kafka contracts.
- **Infrastructure**: in-memory repository + Kafka producer/consumer wrappers.

## Dependency inversion

Business logic depends on interfaces/policies and models, not transport or connector code.
