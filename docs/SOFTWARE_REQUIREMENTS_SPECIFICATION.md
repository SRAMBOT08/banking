# Software Requirements Specification (SRS)

## Purpose
This document defines the functional and non-functional requirements, stakeholders, system boundaries, and design constraints of the Lokii Platform. It outlines the operational standards necessary to support automated security investigations and response actions within enterprise banking ecosystems.

## Overview
Lokii must ingest structured and unstructured telemetry streams, process them through a stateful graph database (Neo4j), analyze links using a LangGraph-orchestrated reasoning agent, calculate deterministic confidence scores, generate immutable audit trails, render multi-format reports via LLM integration (NVIDIA NIM or Gemini), and manage governed mitigation workflows through ServiceNow API calls.

---

## Detailed Explanation

### 1. Introduction & Scope
Lokii serves as an autonomous investigation and containment layer for banking SOC operations. The platform scopes entity extraction (Users, Transactions, Devices, IPs), correlation, threat pattern mapping (MITRE ATT&CK), confidence scoring, report generation, and containment orchestration. It does not replace identity registries or primary core banking ledgers; instead, it consumes telemetry logs to automate security analysis.

### 2. Stakeholders
- **SOC Analysts**: Primary operators who monitor investigations, review timelines, and approve response actions.
- **Security Administrators**: Configure detection rules, integration API keys, and execution policies.
- **Compliance Officers**: Review generated reports and audit trails for regulatory compliance.
- **Platform Engineers/DevOps**: Maintain the system's infrastructure, message queues, and databases.

### 3. Functional Requirements (FR)
- **FR-1: Telemetry Ingestion**: The system must canonicalize raw transaction, asset, and authentication events into a Unified Event Model and publish them to Kafka.
- **FR-2: Entity Correlation**: The Evidence Service must extract IPs, devices, accounts, and transactions, maintaining their relationships in a Neo4j Evidence Graph.
- **FR-3: Threat Pattern Matching**: The Threat Intelligence service must evaluate evidence subgraphs against registered MITRE ATT&CK patterns.
- **FR-4: Stateful Investigation Loop**: The system must initiate a 14-node LangGraph execution loop for each candidate threat, keeping track of history, reasoning nodes, and tool outputs.
- **FR-5: Deterministic Scoring**: Confidence scoring must rely strictly on deterministic code rules, separate from probabilistic LLM outputs.
- **FR-6: Case Packaging**: The Case Builder must package investigation context (evidence, timeline, confidence) into an immutable versioned JSON CaseFile.
- **FR-7: Governed Execution**: The Execution Service must plan containment tasks (e.g., suspend account, block IP) and route them for approval if risk exceeds a defined threshold (e.g., risk score > 40).
- **FR-8: ServiceNow Integration**: The adapter must map execution tasks to ServiceNow REST operations, validating incident creation.

### 4. Non-Functional Requirements (NFR)
- **NFR-1: Performance (Latency)**: API Gateway proxy routing overhead must remain under 10ms. Relational database lookups must complete in under 50ms.
- **NFR-2: Scalability**: The Kafka-driven broker layer must scale horizontally to handle up to 10,000 telemetry events per second.
- **NFR-3: Availability**: Core REST and Kafka consumers must achieve 99.9% uptime, operating inside isolated Docker container environments.
- **NFR-4: Auditability**: Every state transition, node execution, and ServiceNow ticket update must produce a corresponding audit log entry. ServiceNow adapters must protect logs with hash chain integrity chains.

### 5. Assumptions and Constraints
- **Assumptions**: Downstream databases (PostgreSQL, Neo4j) and the Kafka broker are deployed in a shared, secure network environment. LLM providers (NVIDIA NIM or Gemini) are available and reachable over HTTPS.
- **Constraints**: Telemetry payloads must validate against specified Pydantic schemas. Direct database modifications across microservices are forbidden.

---

## Workflow

```
[Raw Telemetry Ingestion]
           │
           ▼
[Deduplication & Verification]
           │
           ▼
[Neo4j Entity Relationship Write]
           │
           ▼
[MITRE Pattern Match Triage]
           │
           ▼
[LangGraph Stateful Investigation]
           │
           ▼
[Deterministic Scoring & Context Building]
           │
           ▼
[CaseFile Serialization]
           │
           ▼
[AI Summary & Mitigation Plan Generation]
           │
           ▼
[ServiceNow Ticket Update & Audit Logging]
```

---

## Design Decisions
- **FastAPI Framework**: Chosen for backend services to leverage async processing and type safety.
- **PostgreSQL and Neo4j Segregation**: Relational entities (Cases, Audits) reside in PostgreSQL, while observed links are maintained in Neo4j.
- **Asynchronous Execution**: Ingestion and investigation paths run on distinct Kafka queues to prevent blockage during large alert spikes.

## Best Practices
- **Schema Enforcement**: Ensure all telemetry fields are strictly typed in Pydantic models.
- **Strict Tenant Scoping**: Scope all database queries and Kafka events with a mandatory `tenant_id` key.
- **Audit Trails**: Never allow database status mutations without writing a corresponding trace record to the audit table.

## Future Enhancements
- Integrate OAuth2/OIDC authentication middleware directly into the API Gateway routing layer.
- Transition the LangGraph memory checkpointer from in-memory MemorySaver to PostgreSQL storage.
