# Database Design Specification

## Purpose
This document specifies the database design, schemas, structures, indexing strategies, and relationships across PostgreSQL, Neo4j, and Redis within the Lokii Platform.

## Overview
Lokii employs a multi-database strategy to align storage characteristics with access patterns. Relational entities (investigations, alerts, cases, audits, policies) reside in PostgreSQL, observed entity relationships are mapped in Neo4j, and session states are cached in Redis.

---

## Detailed Explanation

### 1. Why Multiple Databases?
1. **PostgreSQL**: Used for structured, relational business entities requiring ACID transaction guarantees, such as Cases, Audits, Policies, and Investigation state records.
2. **Neo4j**: Optimized for complex entity link-analysis (e.g. Users, IPs, Transactions, Devices), allowing graph traversals like blast radius queries.
3. **Redis**: Used for low-latency session caching and event deduplication checks in the Ingestion Service.

### 2. PostgreSQL Relational Schemas

#### Investigation Table
Stores the status, metadata, and final results of active investigations.
- `id` (UUID, Primary Key): Unique identifier.
- `status` (VARCHAR, 50): State machine status (e.g. `NEW`, `CLOSED`).
- `priority` (VARCHAR, 20): Priority level (`low`, `medium`, `high`, `critical`).
- `tenant_id` (VARCHAR, 50): Tenant partition ID.
- `final_confidence` (FLOAT, Nullable): Final confidence score.
- `created_at` (TIMESTAMP): Creation time.

#### Audit Table
Tracks changes and actions performed during investigations.
- `id` (UUID, Primary Key): Unique identifier.
- `investigation_id` (UUID, Foreign Key): Links to `Investigation`.
- `action` (VARCHAR, 100): Performed action description.
- `performed_by` (VARCHAR, 100): Operator ID or system agent.
- `timestamp` (TIMESTAMP): Event timestamp.

### 3. Neo4j Graph Schemas
Entities are stored as nodes, and observed telemetry actions are mapped as relationships.

#### Node Types
- `User`: `{id: String, username: String}`
- `Device`: `{id: String, device_type: String}`
- `IP`: `{address: String, asn: String, geo: String}`
- `Account`: `{id: String, currency: String}`
- `Transaction`: `{id: String, amount: Float}`

#### Relationship Types
- `(User)-[:USED_BY]->(Device)`
- `(Device)-[:ASSOCIATED_WITH]->(IP)`
- `(User)-[:OWNS]->(Account)`
- `(Account)-[:CONTAINS]->(Transaction)`

---

## Workflow

```
[Incoming Telemetry]
         │
         ├──► Deduplicate & Cache (Redis)
         │
         ├──► Map Relationships & Links (Neo4j)
         │
         └──► Persist Cases, Status & Audits (PostgreSQL)
```

---

## Design Decisions
- **Loose Coupling**: Services query databases through repository interfaces (e.g. `inmemory` vs `Neo4j-backed`), allowing database replacements without modifying core business logic.
- **Durable Volumes**: Named Docker volumes (`postgres_data`, `neo4j_data`, `redis_data`) ensure data persists across container lifecycles.

## Best Practices
- **Tenancy Partitioning**: Include a mandatory `tenant_id` index in all database tables and queries.
- **Index Optimization**: Apply indexes to foreign key columns (such as `investigation_id` in the `Audit` table) to maintain query performance.
- **Neo4j Traversals**: Restrict path expansion queries in Neo4j to a maximum depth limit (e.g., depth <= 3) to prevent query timeouts.

## Future Enhancements
- Transition process-local memory configurations used in the MVP to database connections.
- Set up Alembic database migrations to manage relational database schemas.
- Implement database replication for enhanced PostgreSQL fault-tolerance.
