# MVP Architecture Specification

## Purpose
This document outlines the scope of the Lokii Platform's MVP (Minimum Viable Product) release. It documents the active simplifications, current capabilities, design limitations, and the integration roadmap for subsequent production releases.

## Overview
The MVP architecture provides a fully functional, containerized, event-driven cybersecurity pipeline designed for local sandbox execution and integration testing. To simplify setup and testing, certain services utilize process-local memory repositories instead of persistent Postgres/Neo4j database connections. However, all API boundaries, schemas, and Kafka event structures reflect production designs.

---

## Detailed Explanation

### 1. Implemented MVP Services
- **Gateway**: Full FastAPI proxy routing and simulation endpoints.
- **Event Simulator**: Cyberspace range simulating banking logins and transfers.
- **Ingestion Service**: Deduplicates telemetry and normalizes payloads to the Unified Event model.
- **Evidence Intelligence**: Extracts entities and maintains relationships in memory.
- **Threat Intelligence**: Validates attack patterns and identifies candidate alerts.
- **Investigation Service**: Core orchestrator running the 14-node LangGraph workflow.
- **Execution Service**: Assembles execution tasks and checks risk policies.
- **ServiceNow Adapter**: Triggers tickets via ServiceNow APIs and logs hash-chained audit traces.
- **Next.js UI Dashboard**: Gathers platform updates, simulations, and details.

### 2. Active Architectural Simplifications
- **In-Memory Storage**: Relational tables (cases, audits, tasks) and graph nodes (Neo4j) utilize local process memory dictionaries in default configurations.
- **LangGraph Checkpoints**: LangGraph states rely on `MemorySaver` in-memory checkpoint managers, meaning active loops do not persist across service restarts.
- **Mock LLM Drivers**: By default, the AI services configure a `mock` provider that generates static text responses, allowing developers to test the stack without active Gemini/NIM API keys.

### 3. Current Limitations
- **Uptime Dependencies**: Restarting the `investigation-service` container clears all active checkpoints and investigation histories.
- **Static Graph traverals**: Neighbor search operations rely on process-local node registers, bypassing active Neo4j container connections in local sandbox configurations.

---

## Workflow

```
[Simulation Triggered]
          │
          ▼
[Memory Ingest Pipelines]
          │
          ▼
[Local Triage Queue]
          │
          ▼
[In-Memory LangGraph Loop]
          │
          ▼
[Transient Case & Report Output]
          │
          ▼
[Mock Execution & Incident Posting]
```

---

## Design Decisions
- **Process-Local Memory Storage (MVP)**: Simplifies local testing by avoiding database migration overhead.
- **Dependency Abstraction**: All database interactions use repository interfaces. This permits switching memory databases to persistent PostgreSQL or Neo4j servers without modifying core service logic.

## Best Practices
- **Configure API Mock Defaults**: Maintain standard mock responses so that developer containers run successfully out-of-the-box.
- **Validate Payload Schemas**: Ensure all transient memory data classes strictly match the API schemas to prevent database migration failures in the future.

## Future Enhancements
- Transition in-memory databases to persistent PostgreSQL and Neo4j servers.
- Replace the LangGraph `MemorySaver` checkpointer with a PostgreSQL-backed checkpointer.
- Set up Alembic database migrations.
