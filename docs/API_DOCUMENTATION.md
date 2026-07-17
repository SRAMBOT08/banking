# API Documentation Specification

## Purpose
This document provides a comprehensive REST API directory for the Lokii Platform. It defines the routes, request schemas, response formats, status codes, and validation parameters across all services.

## Overview
All client interactions map to endpoints exposed by the API Gateway. The Gateway forwards validated requests to the downstream services (Investigation, Case Builder, AI Report, Execution, Simulator, Health). FastAPIs generate interactive documentation automatically at `/docs` or `/openapi.json` for each respective service.

---

## Detailed Explanation

### 1. API Gateway Endpoints
Exposes the central endpoint registry, forwarding requests to downstream services.

#### `GET /api/v1/investigations`
- **Purpose**: Retrieves all investigations.
- **Request**: None.
- **Response (200 OK)**:
  ```json
  [
    {
      "investigation_id": "inv-001",
      "tenant_id": "demo-bank",
      "workflow_status": "COMPLETED",
      "final_confidence": 0.94,
      "severity": "Critical",
      "created_at": "2026-07-16T20:18:56Z"
    }
  ]
  ```

#### `GET /api/v1/investigations/{id}/context`
- **Purpose**: Returns the full investigation details (evidence, timeline, hypotheses, memory, metadata).
- **Request**: Query parameters: `id` (str).
- **Response (200 OK)**:
  ```json
  {
    "investigation_id": "inv-001",
    "evidence": [{"id": "ev-1", "type": "auth"}],
    "hypotheses": [{"name": "account_takeover", "score": 0.94}],
    "final_confidence": 0.94,
    "workflow_status": "COMPLETED"
  }
  ```

#### `POST /api/v1/simulations/run`
- **Purpose**: Triggers a simulation scenario.
- **Request**:
  ```json
  {
    "scenario": "account_takeover",
    "tenant_id": "demo-bank",
    "seed": 1
  }
  ```
- **Response (202 Accepted)**:
  ```json
  {
    "status": "published_scenario",
    "simulation_id": "sim-1234",
    "demo_candidate_status": "published"
  }
  ```

#### `GET /api/v1/platform/health`
- **Purpose**: Gathers health status from all services.
- **Request**: None.
- **Response (200 OK)**:
  ```json
  {
    "services": [
      {
        "service": "gateway",
        "status": "healthy",
        "latency_ms": 12.4
      }
    ]
  }
  ```

### 2. Case Service Endpoints

#### `POST /api/v1/cases/build`
- **Purpose**: Builds an immutable CaseFile from a resolved investigation context.
- **Request**: JSON payload representing `InvestigationContext`.
- **Response (200 OK)**:
  ```json
  {
    "case_id": "550e8400-e29b-41d4-a716-446655440000",
    "title": "Account Takeover",
    "status": "CLOSED",
    "created_at": "2026-07-16T20:18:56Z"
  }
  ```

### 3. AI Report Service Endpoints

#### `POST /api/v1/reports`
- **Purpose**: Generates an incident summary report.
- **Request**:
  ```json
  {
    "case_id": "550e8400-e29b-41d4-a716-446655440000",
    "report_type": "technical"
  }
  ```
- **Response (200 OK)**:
  ```json
  {
    "report_id": "33333333-3333-3333-3333-333333333333",
    "case_id": "550e8400-e29b-41d4-a716-446655440000",
    "content": "AI generated report content...",
    "status": "generated"
  }
  ```

---

## Workflow

```
[Client App] ─── GET /api/v1/investigations ───► [Gateway]
                                                    │
                                                    ▼
[Investigation Svc] ◄── GET /investigations ────────┘
```

---

## Design Decisions
- **Unified Port Architecture**: Downstream microservice ports are isolated inside the Docker network. Client applications communicate only with the Gateway via port `8000`.
- **Automatic Documentation**: FastAPI uses swagger-ui to render API interfaces automatically at `http://localhost:8000/docs` (when exposed).

## Best Practices
- **Strict Validation**: All routes use Pydantic models for request and response body parameters to enforce validation.
- **Unified Error Handling**: Unhandled exceptions are caught by FastAPI exception handlers, returning a structured JSON response:
  ```json
  {"detail": "Error description message."}
  ```

## Future Enhancements
- Secure the public API Gateway endpoints using JWT/OIDC authentication headers.
- Implement rate-limiting headers in the Gateway for enhanced security.
