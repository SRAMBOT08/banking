# System Architecture Specification

## Purpose
This document provides a comprehensive overview of the Lokii Platform's system architecture. It outlines the microservices topology, communication mechanisms, storage layout, event-driven designs, and request/event flows.

## Overview
Lokii uses a decoupled, event-driven microservices architecture built on Docker. System services communicate asynchronously via Kafka topics for event propagation and status tracking. Synchronous REST operations are routed through a FastAPI Gateway proxying traffic to backend endpoints. Storage is separated into relational databases (PostgreSQL), graph databases (Neo4j), and cache structures (Redis).

---

## Architecture

### System Topology Map

```
┌────────────────────────────────────────────────────────────────────────┐
│                              Next.js UI                                │
└──────────────────────────────────┬─────────────────────────────────────┘
                                   │ HTTP / WebSockets
                                   ▼
┌────────────────────────────────────────────────────────────────────────┐
│                          FastAPI API Gateway                           │
└──────────┬───────────────────────┬───────────────────────────────┬─────┘
           │                       │                               │
           ▼                       ▼                               ▼
  ┌─────────────────┐     ┌─────────────────┐             ┌─────────────────┐
  │ Event Simulator │     │  Ingestion Svc  │             │  Investigation  │
  └────────┬────────┘     └────────┬────────┘             └────────┬────────┘
           │                       │                               │
           ▼                       ▼                               ▼
┌────────────────────────────────────────────────────────────────────────┐
│                          Apache Kafka Broker                           │
└──────────┬───────────────────────┬───────────────────────────────┬─────┘
           │                       │                               │
           ▼                       ▼                               ▼
  ┌─────────────────┐     ┌─────────────────┐             ┌─────────────────┐
  │  Evidence Svc   │     │  Threat Intel   │             │   Execution     │
  └────────┬────────┘     └────────┬────────┘             └────────┬────────┘
           │                       │                               │
           ▼                       ▼                               ▼
┌───────────────────────┐ ┌─────────────────┐             ┌─────────────────┐
│     Neo4j Database    │ │   AI Service    │             │   ServiceNow    │
└───────────────────────┘ └─────────────────┘             └─────────────────┘
```

---

## Detailed Explanation

### 1. Gateway Layer
The Gateway acts as the entry point for the frontend, proxying incoming requests to the downstream services:
- **`GET /api/v1/investigations`** → `http://investigation-service:8500/investigations`
- **`GET /api/v1/cases/{id}`** → `http://case-service:8950/api/v1/cases/{id}`
- **`GET /api/v1/platform/health`** → Gathers and returns connection statuses from all services.

### 2. Event-Driven Messaging Layer (Kafka)
The broker handles platform events:
- **`events.unified.v1`**: Transport channel for normalized event structures.
- **`evidence.graph.events.v1`**: Broadcasts updates in the evidence graph.
- **`investigation.candidates.v1`**: Passes triage candidates to the investigation service.
- **`investigations.updated.v1`**: Broadcasts active status modifications.
- **`investigation.completed.v1`**: Initiates execution plan creation.

### 3. Data Storage Layer
- **PostgreSQL**: Stores relational, state-transition, policy, and audit metadata.
- **Neo4j**: Maps physical and logical connections between observed incident actors.
- **Redis**: Caches API responses and normalized event validation states.

### 4. AI Layer
Uses NVIDIA NIM compatibility endpoints (`meta/llama-3.1-70b-instruct`) or Google Gemini API to compile and format incident summaries.

---

## Workflow

### 1. Request Flow (Synchronous)
1. Next.js dashboard requests an investigation context via `GET /api/v1/investigations/{id}/context`.
2. Gateway routes the request to the Investigation Service.
3. Investigation Service queries process-local memory, maps data, and queries Graph/Memory services.
4. Response returns through the Gateway proxy.

### 2. Event Flow (Asynchronous)
1. **Simulation Event**: Event Simulator posts events.
2. **Ingestion**: Ingestion Service parses, validates, and writes events to `events.unified.v1`.
3. **Evidence**: Evidence Service parses facts and updates the Neo4j Evidence Graph.
4. **Threat Intelligence**: Threat Intel runs pattern matches and writes to `investigation.candidates.v1`.
5. **Investigation**: Investigation Service starts the LangGraph Agent, updates PostgreSQL, and publishes to `investigations.updated.v1` and `investigation.completed.v1`.
6. **Case Creation**: Case Builder compiles metadata into CaseFiles.
7. **Execution**: Execution Service evaluates risk policies and issues tickets via ServiceNow.

---

## Design Decisions
- **Microservices Partitioning**: Services are partitioned by context boundaries (e.g. Ingestion vs. Evidence vs. Execution) to support independent deployments.
- **Database Segregation**: Isolates graph operations in Neo4j and transactional cases in PostgreSQL, ensuring optimal database performance.

## Best Practices
- **Isolation**: Services must never access other service databases directly; all state exchanges must flow through APIs or Kafka events.
- **Circuit Breakers**: Outbound API clients use circuit breaker patterns (FastAPI HTTPX wrapper) to handle connection drops.

## Future Enhancements
- Transition in-memory databases used for MVP local dev to persistent PostgreSQL and Neo4j servers.
- Configure WebSocket connections in the Gateway to stream active investigation timelines to the UI.
