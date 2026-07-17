# Security Architecture Specification

## Purpose
This document specifies the security architecture, data boundaries, access control structures, input validation, and audit standards running in the Lokii Platform.

## Overview
Lokii employs a multi-layered security strategy. Network access is restricted through container boundaries, API routes validate requests using Pydantic models, and investigation tools are isolated inside a dedicated runtime environment. In addition, execution activities are audited using hash chain integrity chains to prevent log tampering.

---

## Detailed Explanation

### 1. Network and Container Security
- **Isolation**: Microservices run inside a private Docker bridge network (`sentinel_net`). Only the API Gateway (`8000`) and Frontend UI (`3000`) ports are exposed to host interfaces.
- **Tenancy Boundary**: Data models, database queries, and message payloads are partitioned by customer tenant IDs.

### 2. API Security and Input Validation
- **Pydantic Validation**: All FastAPI entry endpoints validate inputs against strict schemas, filtering out oversized strings and unrecognized fields.
- **CORS Configuration**: The Gateway restricts access to trusted origins (e.g. `http://localhost:3000`).

### 3. Agent Tool Isolation
The LangGraph Agent connects to external tools (Evidence, Threat, Memory) through a dedicated `ToolRouter` boundary. This wrapper:
- Limits operations to a predefined set of REST endpoints.
- Enforces request timeout policies to prevent resource depletion.
- Restricts tool write capabilities, enforcing a read-only execution path.

### 4. Integrity-Chained Audit Logging
The ServiceNow Adapter writes execution logs in JSONL format protected by hash chains to ensure compliance:
- **Hash Chain**: Each log entry contains a hash of its payload combined with the hash of the preceding entry:
  `current_hash = SHA256(payload + previous_hash)`
- **Verification**: If an entry is modified or deleted, the hash chain breaks, allowing administrators to identify audit tampering.

---

## Workflow

```
[Incoming REST Request]
          │
          ▼ (API Gateway checks CORS rules)
[Pydantic Schema Validation]
          │
          ▼ (FastAPI router filters fields)
[Route to downstream service]
          │
          ▼ (Execution logs written)
[Audit Log Entry created with Hash Chain ID]
```

---

## Design Decisions
- **Decoupled Identity Management**: The Gateway acts as a placeholder for identity validation, ensuring OIDC modules can be integrated without modifying downstream microservices.
- **Fail-Safe Defaults**: Threat templates fail to load if structural validation checks identify cyclical references, ensuring the platform starts up in a secure state.

## Best Practices
- **Never Commit Secrets**: Configure database and external API keys using environment variables.
- **Audit State Changes**: Ensure every state mutation publishes an audit event to the `audit.events.v1` topic.

## Future Enhancements
- Implement OAuth2/JWT authentication checks at the Gateway routing layer.
- Encrypt data at rest within PostgreSQL and Neo4j database containers.
- Integrate Kafka SSL configuration to protect internal message payloads.
