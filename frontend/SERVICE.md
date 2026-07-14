Frontend Service Contract

Responsibility:
- UI for investigators and operators. Consumes APIs exposed by Gateway.

Inputs:
- User interactions

Outputs:
- API requests to Gateway

Kafka Topics Produced/Consumed:
- none (frontend communicates via Gateway HTTP/WebSocket)

Database Ownership:
- none

Dependencies:
- shared models for types (TypeScript bindings later)
