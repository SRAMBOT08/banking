# Lokii Platform: Architecture and Technical Documentation

## Project Overview

Lokii is an autonomous, event-driven cybersecurity investigation and decision platform built for enterprise banking security. The platform solves the challenge of high-volume security alerts and complex, manual investigation workflows by automatically processing raw banking telemetry, constructing structured evidence graphs, matching threat indicators, and executing governed response actions. 

Lokii exists to minimize the time-to-resolution for security incidents—such as credential stuffing, account takeover, and insider threats—while ensuring compliance, deterministic policy enforcement, and auditability. It is built for Security Operations Center (SOC) teams, enterprise security architects, and incident response engineers. 

The platform operates on a pipeline that canonicalizes telemetry, extracts entities, constructs relationship graphs, runs a 14-node LangGraph autonomous agent workflow, aggregates confidence scores, structures cases, generates AI reports, and triggers response workflows via ServiceNow.

---

## Table of Contents

- [Project Overview](#project-overview)
- [Architecture Overview](#architecture-overview)
- [Key Features](#key-features)
  - [Investigation](#investigation)
  - [AI](#ai)
  - [Security](#security)
  - [Intelligence](#intelligence)
  - [Reporting](#reporting)
  - [Event Processing](#event-processing)
  - [Execution](#execution)
  - [Monitoring](#monitoring)
- [Technology Stack](#technology-stack)
- [System Architecture](#system-architecture)
- [Repository Structure](#repository-structure)
- [Investigation Workflow](#investigation-workflow)
- [LangGraph Investigation Agent](#langgraph-investigation-agent)
- [Intelligence Layer](#intelligence-layer)
- [Graph Intelligence](#graph-intelligence)
- [Event Driven Architecture](#event-driven-architecture)
- [API Documentation](#api-documentation)
- [Environment Variables](#environment-variables)
- [Installation](#installation)
- [Deployment](#deployment)
- [Database Design](#database-design)
- [Security Architecture](#security-architecture)
- [AI Architecture](#ai-architecture)
- [Frontend](#frontend)
- [Testing](#testing)
- [Logging](#logging)
- [Monitoring](#monitoring-1)
- [Performance](#performance)
- [Design Decisions](#design-decisions)
  - [Why These Technologies?](#why-these-technologies)
- [Contributing](#contributing)
- [Known Limitations](#known-limitations)
- [Future Roadmap](#future-roadmap)
- [License](#license)
- [Acknowledgements](#acknowledgements)

---

## Architecture Overview

Lokii is designed as an asynchronous, event-driven microservices platform. Services communicate primarily through Apache Kafka to ensure decoupling, reliability, and event replay capability. Synchronous communication is handled via REST APIs exposed through a central Gateway. 

The architecture consists of:
- **Frontend**: A Next.js visual dashboard that interfaces with the Gateway.
- **Gateway**: A routing and aggregation proxy exposing public REST endpoints and mock data triggers.
- **Kafka**: The message backbone delivering event payloads between components.
- **Event Simulator**: Generates mock telemetry events mimicking banking transactions and logins.
- **Ingestion Service**: Validates and normalizes raw telemetry events into a unified model.
- **Evidence Intelligence**: Extracts entities and constructs the Evidence Graph in Neo4j.
- **Threat Intelligence**: Validates and registries MITRE ATT&CK patterns and indicators.
- **Knowledge Platform**: Governs attack pattern loading, caching, and matching logic.
- **Graph Intelligence**: Exposes endpoints for traversing nodes, calculating blast radius, and structural queries.
- **Investigation Service**: Orchestrates the core lifecycle state machine and executes the LangGraph agent.
- **LangGraph Agent**: Coordinates reasoning, retrieves context, routes tool calls, and plans responses.
- **Investigation Memory**: Analyzes historical cases and outcome similarity to aid investigation accuracy.
- **Case Builder**: Generates versioned, immutable CaseFiles from resolved investigations.
- **AI Report Service**: Compiles and formats executive, compliance, and technical summaries using LLMs.
- **Execution Service**: Evaluates risk policies and enforces human-in-the-loop approvals.
- **ServiceNow Adapter**: Maps execution tasks to ServiceNow REST operations, validating ticket execution.

System context, sequences, and graph communication flows are defined inside [docs/domain/09_architecture_diagrams.md](file:///c:/Users/Lokesh%20Kumar/OneDrive/Desktop/Github/Cohort_Web_App/banking/docs/domain/09_architecture_diagrams.md).

---

## Key Features

### Investigation
- Stateful, transition-validated investigation lifecycle: `NEW` → `COLLECTING_EVIDENCE` → `PATTERN_MATCHING` → `GRAPH_ANALYSIS` → `HISTORY_ANALYSIS` → `HYPOTHESIS_GENERATION` → `CONFIDENCE_AGGREGATION` → `DECISION_ENGINE` → `WAITING_FOR_APPROVAL` → `REPORT_GENERATION` → `EXECUTION_PLANNING` → `COMPLETED`.
- Bidirectional state mapping: Translates domain models to agent state variables and back.
- Interactive human-in-the-loop checkpoint validation.

### AI
- Stateful reasoning workflows using LangGraph agent orchestration.
- Abstracted LLM provider architecture supporting NVIDIA NIM API-compatible models and Google Gemini API.
- Generates automated executive summaries, SOC briefs, compliance records, and remediation recommendations.

### Security
- Hash chain integrity validation for audit logging of execution adapter tasks.
- Container boundary isolation for distinct microservice scopes.
- Declarative Pydantic model payload validation at all service entry points.

### Intelligence
- Entity resolution and graph-based correlation (linking Users, Devices, IPs, and Accounts).
- MITRE ATT&CK and regulatory fraud pattern matching (e.g., impossible travel, rapid transfer chains).
- Automatic blast radius and centrality metrics calculations.

### Reporting
- Downstream rendering of structured immutable reports.
- Support for Executive, Technical, Compliance, SOC, Root-Cause, and Compliance-Fraud reports.
- Markdown, HTML, JSON, and PDF-ready output formats.

### Event Processing
- Unified schema validation for core event structures.
- Structured Kafka producers and consumers equipped with backoff policies.
- Dedicated Dead Letter Queue (DLQ) routing.

### Execution
- Governed execution planning converting recommendations into step-by-step containment steps.
- Risk-based policy evaluation with thresholds for auto-execution vs. mandatory manual approvals.
- Bi-directional integration verifying ticket state mutations.

### Monitoring
- Automated health check endpoints exposing service operational state.
- Dynamic latency tracking across external dependencies.
- Correlation IDs and investigation IDs propagated throughout logs and traces.

---

## Technology Stack

- **Programming Languages**: Python 3.10+, TypeScript 5.8+
- **Frameworks**: FastAPI, Next.js 15.2.3, React 19.0.0
- **Frontend Libraries**: Material UI (MUI) 6.4.8, Emotion, Zustand 5.0.3, Recharts 2.15.1, Axios 1.8.4, Day.js 1.11.13
- **Backend Core**: Uvicorn, Pydantic (v2.0+), Pydantic Settings, HTTPX, ORJSON, python-json-logger
- **AI Frameworks**: LangGraph, NVIDIA NIM compatible APIs, Google Gemini API
- **Messaging**: Apache Kafka (CP-Kafka 7.4.0), Zookeeper 3.8.1
- **Databases**: PostgreSQL 15, Redis 7 (alpine), Neo4j 5
- **Testing**: Pytest

---

## System Architecture

### Gateway
- **Purpose**: Exposes unified, authenticated entry points for frontend clients and manages downstream service routing.
- **Responsibilities**: Proxying request routes, performing authentication validations, proxying real-time system health checks, and supporting debug event publication.
- **Inputs**: HTTP REST client requests, WebSocket connections.
- **Outputs**: HTTP proxy payloads to internal services, `gateway.audit.v1` events.
- **Dependencies**: `shared` library.
- **Communication Protocol**: HTTP (JSON), WebSocket.
- **Technology Used**: FastAPI, Uvicorn, HTTPX, Confluent-Kafka, Pydantic.

### Ingestion Service
- **Purpose**: Receives external raw telemetry feeds, standardizing and validation before internal broker delivery.
- **Responsibilities**: Telemetry payload canonicalization, schema verification, and event deduplication.
- **Inputs**: External telemetry streams.
- **Outputs**: Canonicalized `events.unified.v1` events.
- **Dependencies**: `shared` library.
- **Communication Protocol**: Kafka (broker client), HTTP.
- **Technology Used**: FastAPI, Confluent-Kafka, Pydantic.

### Event Simulator
- **Purpose**: Simulates production-grade telemetry scenarios to validate incident detection and agent workflows.
- **Responsibilities**: Constructing scenario timelines, injecting background noise, and emitting causal event sequences.
- **Inputs**: REST requests configuring scenarios (e.g., `account_takeover`, `credential_stuffing`).
- **Outputs**: Telemetry events written to `events.unified.v1` or memory transport.
- **Dependencies**: `shared` library.
- **Communication Protocol**: HTTP REST, Kafka.
- **Technology Used**: FastAPI, Confluent-Kafka, Pydantic.

### Evidence Intelligence (evidence-service)
- **Purpose**: Builds the observed entity relationship model from event streams.
- **Responsibilities**: Extracting entities (IPs, accounts, transactions, devices), resolving identities, and writing relationships to Neo4j.
- **Inputs**: `events.unified.v1`.
- **Outputs**: `evidence.graph.events.v1`.
- **Dependencies**: `shared` library, Neo4j.
- **Communication Protocol**: Kafka, Cypher (Neo4j connection).
- **Technology Used**: FastAPI, Confluent-Kafka, Neo4j, Pydantic.

### Threat Intelligence (threat-intelligence-service)
- **Purpose**: Evaluates candidate threat scenarios against current evidence graph events.
- **Responsibilities**: Scanning incoming evidence graphs, mapping detections to MITRE techniques, and pushing potential candidates to the investigation queue.
- **Inputs**: `evidence.graph.events.v1`.
- **Outputs**: `investigation.candidates.v1`.
- **Dependencies**: `shared` library, `evidence-service`.
- **Communication Protocol**: Kafka.
- **Technology Used**: FastAPI, Confluent-Kafka, Pydantic.

### Knowledge Platform (knowledge-service)
- **Purpose**: Maintains versioned attack templates and threat intelligence catalogs.
- **Responsibilities**: Versioned YAML parsing, pattern validation, caching static MITRE details, and servicing pattern lookups.
- **Inputs**: Local template updates, pattern search queries.
- **Outputs**: Static threat context lookup maps, `knowledge.graph.updated.v1` events.
- **Dependencies**: `shared` library.
- **Communication Protocol**: REST APIs.
- **Technology Used**: Busybox placeholder image (local stack), Python core.

### Graph Intelligence (graph-service)
- **Purpose**: Provides graph traversal and graph structural operations.
- **Responsibilities**: Blast radius computations, centrality scoring, subgraph isolation, and structural search logic.
- **Inputs**: Node, neighbor, or path HTTP REST query requests.
- **Outputs**: Graph topology matrices, node linkage lists.
- **Dependencies**: Neo4j.
- **Communication Protocol**: HTTP REST, Cypher.
- **Technology Used**: FastAPI, Neo4j Driver.

### Investigation Memory (memory-service)
- **Purpose**: Provides long-term retrieval and storage of past investigations and outcomes.
- **Responsibilities**: Matching active investigations to past cases, computing similarity matrices, and indexing outcome lessons.
- **Inputs**: Active investigation context profiles.
- **Outputs**: Historical outcome lists, recommendation feedback loops.
- **Dependencies**: REST.
- **Communication Protocol**: HTTP REST.
- **Technology Used**: FastAPI.

### Investigation Service
- **Purpose**: The central processing unit of the platform, orchestrating state machine changes and running the autonomous LangGraph Agent.
- **Responsibilities**: Validating candidates, instantiating orchestrators, invoking LangGraph workflows, persisting state, and publishing lifecycle notifications.
- **Inputs**: `investigation.candidates.v1`.
- **Outputs**: `investigation.active.v1`, `investigation.updated.v1`, `investigation.completed.v1`.
- **Dependencies**: `shared` library, `graph-service`, `memory-service`, `threat-intelligence-service`.
- **Communication Protocol**: Kafka, HTTP REST.
- **Technology Used**: FastAPI, LangGraph, Confluent-Kafka, Pydantic.

### Case Builder (case-service)
- **Purpose**: Packaging service that transforms completed investigation data into structured immutable archives.
- **Responsibilities**: Rendering immutable CaseFiles, managing versioning history, and logging audit logs.
- **Inputs**: REST request with completed InvestigationContext.
- **Outputs**: Serialized versioned `CaseFile` entities, `case.created.v1` events.
- **Dependencies**: `investigation-service`.
- **Communication Protocol**: HTTP REST, Kafka.
- **Technology Used**: FastAPI, Pydantic, Confluent-Kafka.

### AI Report Service
- **Purpose**: Compiles formatted summary documents for regulatory compliance and SOC documentation.
- **Responsibilities**: Managing prompt templates, applying input guardrails, calling LLM API providers, and validating output section requirements.
- **Inputs**: Serialized immutable `CaseFile` entities.
- **Outputs**: HTML, Markdown, or PDF report formats, `report.generated.v1` events.
- **Dependencies**: `case-service` (wire schema boundary compatibility only).
- **Communication Protocol**: HTTP REST, Kafka.
- **Technology Used**: FastAPI, NVIDIA NIM APIs, Pydantic, Confluent-Kafka.

### AI Service (ai-service)
- **Purpose**: Downstream service providing stateless LLM context mapping and text-based reasoning explanations.
- **Responsibilities**: Transforming snapshots into context, prompting models, and validating that confidence values match deterministic outputs.
- **Inputs**: `investigation.snapshot.created.v1` metadata, HTTP requests.
- **Outputs**: `investigation.reasoned.v1`, `investigation.report.generated.v1`, `investigation.ai.metrics.v1`.
- **Dependencies**: `investigation-service`.
- **Communication Protocol**: Kafka, HTTP.
- **Technology Used**: FastAPI, Gemini API, NVIDIA NIM APIs, Pydantic.

### Execution Service
- **Purpose**: Decides and governs containment actions following an investigation.
- **Responsibilities**: Assembling task lifecycles, evaluating rules-based safety policies, and validating approvals.
- **Inputs**: `investigation.completed.v1` event payloads.
- **Outputs**: Execution plan lifecycle events (e.g. `execution.plan.created.v1`, `execution.ready.v1`).
- **Dependencies**: Kafka.
- **Communication Protocol**: Kafka, HTTP REST.
- **Technology Used**: FastAPI, Pydantic, Confluent-Kafka.

### ServiceNow Adapter
- **Purpose**: Handles outbound connections to external ticket systems.
- **Responsibilities**: Creating incidents in ServiceNow, validating record creation, tracking ticket status shifts, and logging hash-chained audit traces.
- **Inputs**: `execution.ready.v1` events.
- **Outputs**: `execution.servicenow.completed.v1` events.
- **Dependencies**: `execution-service`, external ServiceNow instance.
- **Communication Protocol**: HTTP REST, Kafka.
- **Technology Used**: FastAPI, Confluent-Kafka, Pydantic, Hashing algorithms.

### Frontend
- **Purpose**: Web UI providing operations and analytics dashboards for security responders.
- **Responsibilities**: Visualizing dashboards, workspace timelines, graphs, and simulation triggers.
- **Inputs**: User interaction actions, Gateway REST queries.
- **Outputs**: HTTP requests, simulator scenarios launches.
- **Dependencies**: `gateway`.
- **Communication Protocol**: HTTP REST, WebSocket.
- **Technology Used**: React, Next.js, Material UI, Zustand, TanStack Query.

---

## Repository Structure

```
.
├── .github/                               # CI/CD and automation definitions
├── ai-report-service/                     # Downstream report rendering engine
│   ├── app/                               # FastAPI routing and prompt wrappers
│   ├── Dockerfile                         # Build definition
│   ├── SERVICE.md                         # Service contract documentation
│   └── requirements.txt                   # Dependency manifests
├── ai-service/                            # Stateless LLM integration service
│   ├── app/                               # Providers and Prompt builders
│   ├── Dockerfile                         # Build definition
│   ├── SERVICE.md                         # Service contract documentation
│   └── requirements.txt                   # Dependency manifests
├── attack-knowledge-service/              # Manages MITRE ATT&CK patterns mapping
│   ├── app/                               # Context loaders and matching rules
│   ├── Dockerfile                         # Build definition
│   └── requirements.txt                   # Dependency manifests
├── case-service/                          # Generates immutable versioned CaseFiles
│   ├── app/                               # In-memory storage and schemas
│   ├── Dockerfile                         # Build definition
│   ├── SERVICE.md                         # Service contract documentation
│   └── requirements.txt                   # Dependency manifests
├── docker/                                # Sandbox infrastructure files
├── docs/                                  # Platform architecture and ADR repository
│   ├── adr/                               # Architectural Decision Records (ADRs)
│   ├── contracts/                         # API and event schema contracts
│   ├── domain/                            # Business context, sequences, and models
│   └── graphs/                            # Graph structural contracts
├── event-simulator/                       # Telemetry cyber-range simulator
│   ├── app/                               # Scenario models and endpoints
│   ├── Dockerfile                         # Build definition
│   ├── SERVICE.md                         # Service contract documentation
│   └── requirements.txt                   # Dependency manifests
├── evidence-service/                      # Extracts facts, updates Neo4j evidence graph
│   ├── app/                               # Kafka consumption and graph repo interfaces
│   ├── Dockerfile                         # Build definition
│   ├── SERVICE.md                         # Service contract documentation
│   └── requirements.txt                   # Dependency manifests
├── execution-service/                     # Execution planner, governance, and policy
│   ├── app/                               # Policy validation and planning rules
│   ├── Dockerfile                         # Build definition
│   ├── SERVICE.md                         # Service contract documentation
│   └── requirements.txt                   # Dependency manifests
├── frontend/                              # Visual Next.js application
│   ├── src/                               # MUI views (Dashboard, Workspace, Simulator)
│   ├── Dockerfile                         # Production web deployment definition
│   ├── SERVICE.md                         # Frontend communication contract
│   └── package.json                       # JavaScript package declarations
├── gateway/                               # Unified proxy router and CORS manager
│   ├── app/                               # REST forwards and simulation endpoints
│   ├── Dockerfile                         # Build definition
│   ├── SERVICE.md                         # API routing contract
│   └── requirements.txt                   # Dependency manifests
├── graph-service/                         # Exposes endpoints for graph operations
│   ├── app/                               # Traversal, neighborhood, and blast radius logic
│   ├── Dockerfile                         # Build definition
│   └── requirements.txt                   # Dependency manifests
├── ingestion-service/                     # Validates raw telemetry feeds
│   ├── app/                               # Deduplication filters and schemas
│   ├── Dockerfile                         # Build definition
│   ├── SERVICE.md                         # Ingestion contract documentation
│   └── requirements.txt                   # Dependency manifests
├── integration/                           # Staging validator frameworks
├── investigation-service/                 # Core service running LangGraph Agent
│   ├── app/                               # State mappers, planners, and node handlers
│   ├── Dockerfile                         # Build definition
│   ├── SERVICE.md                         # Investigation lifecycle contract
│   └── requirements.txt                   # Dependency manifests
├── memory-service/                        # Query API for past investigations similarities
│   ├── app/                               # Vector-like in-memory lookups
│   ├── Dockerfile                         # Build definition
│   └── requirements.txt                   # Dependency manifests
├── servicenow-adapter/                    # Outbound ServiceNow REST integration
│   ├── app/                               # Auth providers and incident poster
│   ├── Dockerfile                         # Build definition
│   ├── SERVICE.md                         # Incident creation contract
│   └── requirements.txt                   # Dependency manifests
├── shared/                                # Monolithic Python shared SDK
│   ├── common/                            # Core exceptions and formatters
│   ├── config/                            # Global settings parsers
│   ├── models/                            # Shared domain data classes
│   └── pyproject.toml                     # Python packaging config
├── tests/                                 # Centralized verification test suite
│   ├── Dockerfile.test                    # Test-runner image definition
│   └── test_platform_integration_sdk.py   # System validation checks
├── threat-intelligence-service/           # Handles indicator evaluation
│   ├── app/                               # Pattern loading and matching interfaces
│   ├── Dockerfile                         # Build definition
│   ├── KNOWLEDGE_PLATFORM.md              # RegistryManager architectural outline
│   └── requirements.txt                   # Dependency manifests
└── docker-compose.yml                     # Main environment definition
```

---

## Investigation Workflow

```
Attack Simulator
      │
      ▼ (HTTP POST /api/v1/simulations/run)
    Kafka (investigation.candidates.v1)
      │
      ▼
Ingestion Service (Schema Validation & Deduplication)
      │
      ▼ (events.unified.v1)
Evidence Intelligence (Entity Extraction & Neo4j Write)
      │
      ▼ (evidence.graph.events.v1)
Threat Intelligence (Registry Pattern Scan)
      │
      ▼ (investigation.candidates.v1)
Knowledge Platform (Lookup ATT&CK Ontology)
      │
      ▼
Graph Intelligence (Centrality & blast-radius REST call)
      │
      ▼
Investigation Agent (LangGraph 14-Node Stateful Reasoning Loop)
      │
      ▼ (updates Investigation domain state in Postgres)
Case Builder (Serializes final context to Immutable CaseFile)
      │
      ▼ (case.created.v1)
AI Report Service (LLM Prompting via NVIDIA NIM/Mock)
      │
      ▼ (report.generated.v1)
Execution Service (Risk policy checks & task planning)
      │
      ▼ (execution.ready.v1)
ServiceNow Adapter (ServiceNow REST API POST & verification check)
```

### Stage Explanations
1. **Attack Simulation**: Triggered on the UI or API, launching scenarios like `account_takeover`.
2. **Kafka Delivery**: Telemetry triggers are pushed to Kafka brokers on designated topics.
3. **Ingestion**: Payload schema fields are validated against strict structural rules.
4. **Evidence Intelligence**: The service extracts IP addresses, transaction records, accounts, and devices, building nodes in the Neo4j Evidence Graph.
5. **Threat Intelligence**: Analyzes the graph structure to check for known signatures or anomalous transitions.
6. **Knowledge Platform**: Attaches MITRE mappings (like T1110 for brute force) to the candidate data.
7. **Graph Intelligence**: Calculates centrality scores and retrieves community clusters.
8. **Investigation Agent**: The stateful engine executes a sequence of 14 nodes, determining confidence and drafting mitigation plans.
9. **Case Builder**: Locks the investigation timeline and findings into a versioned JSON CaseFile structure.
10. **AI Report**: A downstream LLM generates technical and executive summaries.
11. **Execution**: Assesses risks against criteria; alerts operators if manual approval is required.
12. **ServiceNow**: Translates containment tasks (e.g., suspend account) into ServiceNow tickets and audits compliance.

---

## LangGraph Investigation Agent

Lokii leverages LangGraph to orchestrate stateful AI-driven security investigations. 

### Why LangGraph & Stateful Workflows?
Incident response processes are non-linear. They require looping (re-collecting evidence), conditional branches (determining if human approval is necessary), and checkpoints (saving state to allow manual override and resumption). LangGraph provides a robust, state-backed engine to compile complex directed graphs, preventing the fragility of single-prompt LLM agents.

### The 14-Node Stateful Loop
```
             START
               │
               ▼
       [collect_evidence] ◄────────────────────────────────┐
               │                                           │
               ▼                                           │
      [retrieve_knowledge]                                 │
               │                                           │
               ▼                                           │ (collect_more)
     [run_pattern_matching]                                │
               │                                           │
    [identify_missing_evidence] ──(evidence_route)─────────┤
               │                                           │
               ▼ (continue)                                │
        [graph_analysis]                                   │
               │                                           │
               ▼                                           │
       [retrieve_history]                                  │
               │                                           │
               ▼                                           │
      [generate_hypotheses]                                │
               │                                           │
               ▼                                           │
     [aggregate_confidence]                                │
               │                                           │
       [decision_engine] ──(decision_route)────────────────┘
               │
               ├───────────────────────┬───────────────────┐
               ▼ (approval)            ▼ (continue)        ▼ (more_evidence)
          [checkpoint]          [build_investigation]   [collect_evidence]
               │                       │
               ▼                       ▼
       [human_approval]        [generate_ai_report]
               │                       │
       (approval_route)                ▼
        ├── wait ──► [human_app] [execution_planning]
        └── resume ──► [build_inv]     │
                                       ▼
                                      END
```

### Components
- **InvestigationState**: Tracks investigation details, lists of evidence, hypotheses, confidence metrics, and node execution times.
- **Workflow Engine**: Manages transition pathways, ensuring actions follow the defined state machine constraints.
- **Reasoning Engine**: Checks if collected facts are sufficient to support a selected hypothesis.
- **Tool Router**: Dispatches calls to isolated tool adapters (evidence, threat, graphs).
- **Hypothesis Manager**: Ranks suspect scenarios and manages their confidence values.
- **Confidence Manager**: Performs deterministic score tracking based on present indicators.
- **Checkpoint Manager**: Saves snapshots of the InvestigationState to permit pauses and rollbacks.
- **Investigation Memory**: Looks up past incident profiles to check for repeating matches.

### NVIDIA NIM Integration
The AI nodes communicate with NIM API endpoints (e.g. `meta/llama-3.1-70b-instruct`) to generate natural language explanations and summaries without making system changes.

### LLM vs. Deterministic Boundaries
- **Deterministic Logic**: Graph traversals, confidence calculations, policy comparisons, and state transitions are handled mathematically by the platform codebase.
- **LLM Logic**: Summarization, scenario descriptions, and text-based recommendation rationales.

---

## Intelligence Layer

The platform is structured with distinct intelligence components:
- **Evidence Intelligence**: Authoritative boundary for observed actions. Translates raw telemetry into graph representations, keeping track of ingestion logs.
- **Threat Intelligence**: Validates patterns and maps indicators to specific threat signatures.
- **Knowledge Platform**: Houses in-memory attack models, checking template DAGs for cycles during startup.
- **Graph Intelligence**: Exposes endpoints for computing graph metrics like Blast Radius.
- **Investigation Memory**: Retains records of resolved cases to suggest past incident containment outcomes.

---

## Graph Intelligence

### Why Neo4j & Graph Databases?
Security telemetry is highly relational. A single IP address might link to multiple user sessions, which map to distinct devices and bank accounts. Relational databases require complex join queries to trace these paths, whereas Neo4j handles multi-hop traversal instantly, enabling real-time blast radius calculations.

### Node and Relationship Types
- **Nodes**: `User`, `Customer`, `Account`, `Transaction`, `Device`, `IP`, `Threat Indicator`, `Asset`.
- **Relationships**: `OWNS`, `CONTAINS`, `RELATED_TO`, `SENT_TO`, `INITIATED_BY`, `USED_BY`, `ASSOCIATED_WITH`, `MATCHES`, `MAPPED_TO`, `PART_OF`, `LINKS_TO`.

### Traverse Logic
Graph algorithms execute traversals to isolate connected subgraphs. When the Agent calls `/api/v1/graph/blast-radius/{node_id}`, the query layer traces outbound linkages up to a configured depth to measure the scope of exposure.

---

## Event Driven Architecture

```
                  ┌─────────────────┐
                  │ Event Simulator │
                  └────────┬────────┘
                           │ events.unified.v1
                           ▼
                  ┌─────────────────┐
                  │  Ingestion Svc  │
                  └────────┬────────┘
                           │ events.unified.v1
                           ▼
 ┌───────────────┐     ┌───┴───┐     ┌────────────────┐
 │ Evidence Serv │◄────┤ Kafka ├────►│ Investigation  │
 └───────┬───────┘     └───┬───┘     └───────┬────────┘
         │                 │                 │
         │ evidence.graph  │                 │ investigations.updated.v1
         │ .events.v1      │                 ▼
         └─────────────────┼────────────────►┌────────────────┐
                           │                 │   AI Service   │
                           │                 └────────────────┘
                           │ case.created.v1
                           ▼
                  ┌─────────────────┐
                  │  Case Service   │
                  └────────┬────────┘
                           │ case.created.v1
                           ▼
                  ┌─────────────────┐
                  │ AI Report Serv  │
                  └─────────────────┘
```

### Kafka Topics
- `events.unified.v1`: Canonical telemetry messages (Ingestion -> Evidence / Investigation).
- `events.unified.dlq.v1`: Ingest failures redirected for inspection.
- `evidence.graph.events.v1`: Emitted when evidence structures update.
- `investigation.candidates.v1`: Queue containing alerts that need triage.
- `investigations.updated.v1`: Broadcasts active status modifications.
- `investigation.completed.v1`: Sent when an investigation successfully concludes.
- `case.created.v1`: Announces CaseFile creation.
- `report.generated.v1`: Sent when AI report compilation finishes.
- `execution.ready.v1`: Triggers downstream integrations like ServiceNow.

### Retry & Partitioning
- **Retries**: Consumers implement three retry attempts with exponential backoff before sending the message to the Dead Letter Queue.
- **Ordering**: Event IDs are used as partition keys to ensure related telemetry processes sequentially.

---

## API Documentation

### Gateway APIs
- `GET /health`: Checks gateway status.
- `GET /api/v1/investigations`: Lists all active investigations.
- `GET /api/v1/investigations/{id}/context`: Retrieves the full context model.
- `GET /api/v1/cases/{id}`: Returns CaseFile payload.
- `POST /api/v1/simulations/run`: Triggers simulation scenarios.

### Investigation APIs
- `GET /investigations`: Returns all investigations.
- `GET /investigations/{id}/snapshots`: Lists immutable context states.

### Case Builder APIs
- `POST /api/v1/cases/build`: Assembles CaseFiles.
- `GET /api/v1/cases/{id}/versions`: Accesses change tracking history.

### AI Report APIs
- `POST /api/v1/reports`: Submits requests for report generation.
- `GET /api/v1/reports/{id}`: Downloads rendered files.

### Execution APIs
- `GET /execution/status`: Accesses planning worker states.

FastAPI endpoints generate interactive documentation automatically, accessible at `/docs` or `/openapi.json` for each respective service.

---

## Environment Variables

| Variable | Required | Description | Default |
|----------|----------|-------------|---------|
| `KAFKA_BOOTSTRAP_SERVERS` | Yes | Kafka broker connection details | `kafka:9092` |
| `REDIS_URL` | Yes | Connection string for Redis instance | `redis://redis:6379/0` |
| `POSTGRES_USER` | Yes | Relational database username | `postgres` |
| `POSTGRES_PASSWORD` | Yes | Relational database password | `postgres` |
| `POSTGRES_DB` | Yes | Relational database name | `sentinel` |
| `NEO4J_AUTH` | Yes | Graph authentication settings | `neo4j/testpassword` |
| `LLM_PROVIDER` | No | Target LLM driver selection | `mock` |
| `GEMINI_API_KEY` | No | Access token for Google Gemini | `None` |
| `NIM_ENDPOINT` | No | Connection URL for NVIDIA NIM inference | `http://nim:8000/v1` |
| `NIM_MODEL` | No | Target NVIDIA NIM model identifier | `meta/llama-3.1-70b-instruct` |

---

## Installation

### Prerequisites
- Docker (v20.10+)
- Docker Compose (v2.0+)
- Python 3.10+ (if configuring local services)

### Step 1: Clone the Repository
```bash
git clone <repository_url>
cd banking
```

### Step 2: Configure the Environment
Create a `.env` file from the provided example:
```bash
cp .env.example .env
```

### Step 3: Run with Docker Compose
Build and start the complete service stack:
```bash
docker compose up -d --build
```

---

## Deployment

### Service Startup Order
To prevent connection errors, the stack starts up in a controlled sequence:
1. `zookeeper` and `kafka` start.
2. `postgres`, `neo4j`, and `redis` start.
3. Microservices start once dependency health checks pass.
4. `frontend` starts last, connecting via the proxy Gateway.

### Volumes and Networking
- **sentinel_net**: A bridge network isolates service communications.
- **Durable Volumes**: Named volumes preserve data across restarts: `postgres_data`, `neo4j_data`, `redis_data`, `kafka_data`.

---

## Database Design

```
           [PostgreSQL Relational Schema]
  ┌─────────────────┐             ┌─────────────────┐
  │  Investigation  │1           *│      Audit      │
  │  - id (PK)      ├────────────►│  - id (PK)      │
  │  - status       │             │  - action       │
  │  - priority     │             │  - timestamp    │
  └────────┬────────┘             └─────────────────┘
           │1
           │
           │*
  ┌────────▼────────┐             ┌─────────────────┐
  │   Hypothesis    │1           *│    Evidence     │
  │  - id (PK)      ├────────────►│  - id (PK)      │
  │  - name         │             │  - type         │
  │  - confidence   │             │  - value        │
  └─────────────────┘             └─────────────────┘

            [Neo4j Evidence Graph Schema]
       (User) ───[USED_BY]───► (Device) ───[ASSOCIATED_WITH]───► (IP)
         │                                                        │
      [OWNS]                                                  [MATCHES]
         │                                                        │
         ▼                                                        ▼
     (Account) ───[CONTAINS]───► (Transaction)           (Threat Indicator)
```

- **PostgreSQL**: Stores relational, state-transition, policy, and audit metadata.
- **Neo4j**: Maps physical and logical connections between observed incident actors.
- **Redis**: Caches API responses and normalized event validation states.

---

## Security Architecture

- **Authentication / Authorization**: Decoupled design; the Gateway acts as a placeholder for OIDC authentication.
- **LLM Input Guardrails**: The AI services parse inputs to block prompt injection and size violations.
- **Container Isolation**: Services run inside lightweight containers with minimal privilege.
- **Tool Isolation**: The LangGraph Agent can only interface with external resources through the registered endpoints inside the `ToolRouter` boundary.
- **Audit Logging**: The ServiceNow Adapter logs activities in append-only JSONL files protected by hash chains to ensure compliance.

---

## AI Architecture

```
           Investigation Candidate Ingested
                          │
                          ▼
           StateMapper.to_agent_state()
                          │
                          ▼
             LangGraph execution starts
                          │
         ┌────────────────┴────────────────┐
         ▼                                 ▼
   ToolRouter Calls                Reasoning Node (NIM)
   (Evidence, Graph, Memory)       - Explains correlations
         │                         - Outlines threat severity
         │                                 │
         ▼                                 ▼
   State Update                      State Update
         │                                 │
         └────────────────┬────────────────┘
                          │
                          ▼
            StateMapper.from_agent_state()
                          │
                          ▼
           Persist Relational State Changes
```

The platform AI architecture coordinates LangGraph's state graph execution with NIM LLM endpoints to automate analysis without losing auditability.

---

## Frontend

The user interface is built on Next.js and Material UI (MUI).

### Page Components
- **Overview Dashboard**: Displays high-level KPIs, threat activity, and system health status.
- **Investigations Workspace**: Lists active triage items, detailing confidence, severity, and status.
- **Investigation Workspace Detail**: Exposes evidence, interactive relationship subgraphs, and generated AI reports.
- **Attack Simulator Panel**: Allows operators to launch test scenarios and watch the pipeline progress.
- **System Health**: Details real-time connection status and latency charts for system dependencies.

---

## Testing

The platform includes unit tests and integration tests.

### How to Run Tests
To run all tests inside a test container:
```bash
docker compose --profile test up --build test-runner
```
To run tests locally:
```bash
pytest tests/
```

### Coverage
Test suites validate event routing, state transitions, tool registry mapping, and ServiceNow endpoint handling.

---

## Logging

Logging is structured using `python-json-logger` to export records in JSON format:
```json
{"timestamp": "2026-07-16T20:18:56Z", "level": "INFO", "event": "tool_completed", "tool": "graph", "duration_ms": 12.4, "correlation_id": "cor-9e4b1"}
```
Correlation IDs are passed through header metadata to track events from ingestion to resolution.

---

## Monitoring

- **Health Checks**: Every service exposes a `/health` REST endpoint returning status.
- **Status Panel**: The frontend monitors service status and response latency.
- **Logging Traces**: Event handlers log exceptions to help isolate pipeline blockages.

---

## Performance

- **Independent Scaling**: Services scale independently behind Kafka brokers.
- **Asynchronous Execution**: Ingestion operations run asynchronously to prevent ingestion blockages.
- **In-Memory Caching**: Redis instances cache active data parameters to lower graph database load.

---

## Design Decisions

### Why These Technologies?
- **FastAPI**: Provides high execution performance and automatic OpenAPI generation.
- **React (Next.js)**: Supports quick dashboard rendering and modular visual components.
- **Apache Kafka**: Ensures reliable message delivery and event replay options.
- **LangGraph**: Enables stateful reasoning loops with loop-back and execution pause logic.
- **PostgreSQL**: Reliable transactional persistence for case records.
- **Neo4j**: Native, fast graph traversing to check blast radius.
- **Docker**: Simplifies deployment and guarantees local runtime parity.
- **NVIDIA NIM**: Optimizes local token processing speeds.
- **Microservices**: Isolates service failures and supports language-agnostic components.

---

## Contributing

1. **Coding Standards**: Adhere to PEP 8 standards, and define Pydantic models for data interfaces.
2. **Branching**: Submit PRs to the `main` branch.
3. **Commit Messages**: Follow standard patterns: `[Service Name] Short description`.

---

## Known Limitations

- **In-Memory Defaults**: To simplify development, some services default to process-local repositories instead of database connections.
- **Memory Checkpointing**: The LangGraph Agent uses `MemorySaver`, meaning active graph states do not persist across service restarts.

---

## Future Roadmap

- **Persistent Checkpointing**: Transition LangGraph states to PostgreSQL storage.
- **Durable Storage**: Replace local-memory repositories with permanent database implementations.
- **Alembic migrations**: Configure database schema migrations for relational tables.
- **Real-Time Updates**: Implement WebSockets to sync frontend displays automatically.

---

## License

This project is licensed under the MIT License. See [LICENSE](file:///c:/Users/Lokesh%20Kumar/OneDrive/Desktop/Github/Cohort_Web_App/banking/LICENSE) for details.

---

## Acknowledgements

- Lokii Development Team
- LangGraph and LangChain Contributors
- NVIDIA NIM API Team
