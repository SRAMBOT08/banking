# Architecture Decisions Specification (ADR)

## Purpose
This document provides architectural rationales (ADRs) for selecting the core technologies running in the Lokii Platform. It documents the problem statements, alternatives, selection criteria, benefits, and tradeoffs for each design decision.

## Overview
All technological selections prioritize system performance, developer workflow efficiency, database separation, and strict separation between deterministic calculations and AI reasoning layers.

---

## Detailed Explanation

### 1. ADR-001: FastAPI for Backend Services
- **Problem**: Need to build lightweight, high-performance REST APIs with built-in input validation.
- **Alternatives**: Flask, Django, Express.js.
- **Selection Reason**: FastAPI supports async processing natively and uses Pydantic for data validation.
- **Tradeoffs**: Requires a python runtime; relatively newer ecosystem than Django.
- **Benefits**: Automatic OpenAPI documentation generation, fast execution speeds, and type validation out-of-the-box.

### 2. ADR-002: Apache Kafka for Messaging
- **Problem**: Decoupling services while supporting independent scaling and event replay.
- **Alternatives**: RabbitMQ, Amazon SQS, gRPC.
- **Selection Reason**: Kafka is designed for high-throughput, partitioned event streaming, and logs retention.
- **Tradeoffs**: Higher operational setup complexity than RabbitMQ.
- **Benefits**: Supports event replay, consumer grouping, and message partitioning.

### 3. ADR-003: Neo4j for Graph Storage
- **Problem**: Storing and traversing highly connected security telemetry facts.
- **Alternatives**: PostgreSQL JOIN tables, MongoDB.
- **Selection Reason**: Neo4j is a native graph database, optimizing multi-hop traversals and blast radius queries.
- **Tradeoffs**: Requires learning Cypher; represents another database dependency in the stack.
- **Benefits**: Rapid path execution, visual relationship modeling, and native graph algorithms.

### 4. ADR-004: PostgreSQL for Relational Data
- **Problem**: Storing structured, business-critical cases, audit logs, and status records requiring transactional guarantees.
- **Alternatives**: MySQL, DynamoDB.
- **Selection Reason**: PostgreSQL is a mature, ACID-compliant relational database.
- **Tradeoffs**: Requires database schema management.
- **Benefits**: Rich indexing options, relational consistency, and extensive integration support.

### 5. ADR-005: LangGraph for Agent Orchestration
- **Problem**: Building complex, non-linear investigation agent workflows with cycles and interruptions.
- **Alternatives**: LangChain Agents, AutoGen, CrewAI.
- **Selection Reason**: LangGraph allows defining workflows as state graphs, supporting cycles, checkpoints, and conditional routing.
- **Tradeoffs**: Higher learning curve than standard linear agents.
- **Benefits**: Factual tracking, easy debugging, and built-in support for human-in-the-loop validation.

### 6. ADR-006: NVIDIA NIM for AI Report Generation
- **Problem**: Generating natural language summaries and reports without vendor lock-in.
- **Alternatives**: OpenAI API, local Hugging Face pipelines.
- **Selection Reason**: NVIDIA NIM provides self-hosted, optimized inference endpoints compatible with standard chat-completion APIs.
- **Tradeoffs**: Requires local GPU acceleration for host deployments.
- **Benefits**: Low response latency and high model deployment flexibility.

---

## Workflow

```
[New Technology Proposal]
           │
           ▼
[Evaluate Alternatives & Tradeoffs]
           │
           ▼
[Draft ADR Specification Document]
           │
           ▼
[Submit for Architecture Board Review]
```

---

## Design Decisions
- **Fail-Safe Validation**: Structural issues or cycle loops in loaded templates raise a `RegistryValidationError`, causing the service startup to fail closed.
- **Isolated AI Layer**: AI integrations are restricted to report generation and text explanations, keeping decisions and confidence scoring deterministic.

## Best Practices
- **Write ADRs Proactively**: Document architectural decisions before starting implementation.
- **Limit Dependencies**: Evaluate open-source frameworks to minimize vendor lock-in.

## Future Enhancements
- Set up automated ADR status tracking scripts to monitor database changes.
- Add Helm Chart deployment specs to standard deployment decisions.
