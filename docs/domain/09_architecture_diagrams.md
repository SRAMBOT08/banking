# 09 — Architecture Diagrams (Mermaid)

## System Context

```mermaid
flowchart TB
  ExternalSystems[External Systems]
  Kafka[(Kafka)]
  Ingestion[Ingestion Service]
  Evidence[Evidence Service]
  Knowledge[Knowledge Service]
  Investigation[Investigation Service]
  AI[AI Service]
  Execution[Execution Service]
  Gateway[API Gateway]
  Frontend[Frontend UI]

  ExternalSystems -->|events| Kafka
  Kafka --> Ingestion
  Ingestion -->|events.unified.v1| Evidence
  Knowledge -->|knowledge.graph.updated.v1| Investigation
  Evidence -->|evidence.graph.events.v1| Investigation
  Investigation -->|investigations.updated.v1| AI
  Investigation -->|execution.requests.v1| Execution
  Frontend -->|HTTP/WebSocket| Gateway -->|API| Investigation
```

## Kafka Flow

```mermaid
sequenceDiagram
  participant Ingestion
  participant Kafka
  participant Evidence
  participant Investigation
  participant AI
  Ingestion->>Kafka: events.unified.v1
  Kafka->>Evidence: deliver
  Evidence->>Kafka: evidence.graph.events.v1
  Kafka->>Investigation: deliver
  Investigation->>Kafka: investigations.updated.v1
  Investigation->>AI: context request (via topic)
  AI->>Kafka: ai.responses.v1
```

## Investigation Flow

```mermaid
flowchart LR
  Alert --> Investigation
  Investigation --> Evidence
  Investigation --> AI
  AI --> Recommendation
  Recommendation --> Execution
  Execution --> Ticket
```

## Evidence Lifecycle

```mermaid
flowchart TB
  RawEvent --> Ingestion
  Ingestion --> NormalizedEvent
  NormalizedEvent --> EvidenceService
  EvidenceService --> EvidenceGraph
  EvidenceGraph --> Investigation
```

Notes: diagrams render with Mermaid; keep them updated as ADRs evolve.
```
