# SentinelIQ Integrated Architecture

```mermaid
flowchart LR
  S[Enterprise Event Simulator] --> K[(Kafka events.unified.v1)]
  K --> I[Ingestion]
  I --> E[Evidence Intelligence]
  E --> T[Threat Intelligence]
  E --> KNO[Knowledge Platform]
  E --> G[Graph Intelligence]
  E --> M[Investigation Memory]
  T --> A[Intelligence Aggregator]
  KNO --> A
  G --> A
  M --> A
  A --> AG[Investigation Agent]
  AG --> C[Case Builder]
  C --> R[AI Report Service]
  C --> X[Execution Service]
  R --> X
  X --> SN[ServiceNow Adapter]
```

The dotted/HTTP-style downstream links are represented as directed edges in the diagram; the integration harness validates their payload contracts without requiring all infrastructure containers.
