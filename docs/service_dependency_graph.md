# Service Dependency Graph

```mermaid
graph TD
  simulator[event-simulator] --> kafka[Kafka]
  kafka --> ingestion[ingestion-service]
  ingestion --> evidence[evidence-service]
  evidence --> threat[threat-intelligence-service]
  evidence --> knowledge[knowledge-service]
  evidence --> graph[graph-service]
  evidence --> memory[memory-service]
  threat --> investigation[investigation-service]
  knowledge --> investigation
  graph --> investigation
  memory --> investigation
  investigation --> case[case-service]
  case --> report[ai-report-service]
  case --> execution[execution-service]
  report --> execution
  execution --> adapter[servicenow-adapter]
  adapter --> snow[ServiceNow]
```

The graph describes intended ownership and dependencies. The contract validation report identifies links that still need live Kafka/HTTP wiring in Docker.
