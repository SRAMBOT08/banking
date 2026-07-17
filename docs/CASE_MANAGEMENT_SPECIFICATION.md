# Case Management Specification

## Purpose
This document specifies the case management design, serialization schemas, immutable snapshot contracts, audit logging standards, and versioning rules implemented in the Lokii Platform.

## Overview
Case management is governed by the Case Builder Service (`case-service`). The service packages completed investigation details into an immutable, versioned JSON `CaseFile`. The Case Builder is a record-keeping service; it does not call external LLMs or perform dynamic reasoning.

---

## Detailed Explanation

### 1. The Immutable CaseFile Schema
A completed investigation context is serialized into a versioned `CaseFile` payload:

```json
{
  "case_id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "Account Takeover Scenario Triage",
  "status": "CLOSED",
  "tenant_id": "demo-bank",
  "investigation_id": "inv-1234",
  "final_confidence": 0.94,
  "severity": "Critical",
  "version": 1,
  "evidence_records": [
    {
      "evidence_id": "123-auth",
      "type": "authentication_event",
      "timestamp": "2026-07-16T20:18:56Z"
    }
  ],
  "timeline_events": [
    {
      "timestamp": "2026-07-16T20:18:56Z",
      "event": "node_start",
      "message": "collect_evidence node started execution"
    }
  ],
  "audit_trail": [
    {
      "timestamp": "2026-07-16T20:18:56Z",
      "action": "case_compiled",
      "operator": "case-builder-service"
    }
  ]
}
```

### 2. Versioning and Immutable Snapshots
- **Immutability**: Once compiled, CaseFiles are read-only.
- **Snapshots**: The Snapshot Engine handles snapshots, managed by `SnapshotManager` inside the Investigation Service. Snapshots are transient, never written directly to database storage, and copy on write and read.
- **Versioning**: Subsequent edits or operator notes increment the `version` field (e.g. Version 1 → Version 2), saving the updated state as a new entry to preserve history.

### 3. API Directory
- **`POST /api/v1/cases/build`**: Assembles CaseFiles from investigation contexts.
- **`GET /api/v1/cases/{id}`**: Returns the latest CaseFile version.
- **`GET /api/v1/cases/{id}/versions`**: Lists all available versions.
- **`GET /api/v1/cases/{id}/audit`**: Accesses the audit log history.

---

## Workflow

```
[Investigation Concludes]
            │
            ▼ (investigation.completed.v1)
[Call Case Service api/v1/cases/build]
            │
            ▼
[Deduplicate and Parse Context]
            │
            ▼
[Compile Immutable JSON CaseFile]
            │
            ▼
[Save to Repository & Emit case.created.v1]
```

---

## Design Decisions
- **Packaging Boundary**: The Case Builder maintains a separate deployment boundary from the investigation service, ensuring CaseFiles remain accessible even during investigation agent downtime.
- **Transient Snapshots**: Snapshots are designed as process-local transient memory arrays to protect data from direct file access mutations.

## Best Practices
- **Never Modify Cases**: Always treat CaseFile payloads as read-only. Save modifications as a new version.
- **Verify Signatures**: Ensure CaseFiles contain complete audit entries detailing the compiling service.

## Future Enhancements
- Transition local-memory storage structures to PostgreSQL case tables.
- Add support for digital signatures to verify CaseFile integrity.
