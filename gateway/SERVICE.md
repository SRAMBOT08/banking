Gateway Service Contract

Responsibility:
- API routing, authentication middleware placeholder, aggregation, websocket gateway

Inputs:
- REST requests from clients
- Authentication tokens (external)

Outputs:
- Forwards validated requests to backend services
- Publishes gateway events (audit, request received) to Kafka (contract only)

Kafka Topics Produced:
- gateway.audit.v1

Kafka Topics Consumed:
- none in Phase 1 (gateway forwards only)

Database Ownership:
- none (gateway is stateless)

External Integrations:
- Identity provider (placeholder)

Dependencies:
- shared library

Shared Models Used:
- shared.models.http.*
