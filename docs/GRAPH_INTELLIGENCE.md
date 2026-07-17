# Graph Intelligence Specification

## Purpose
This document specifies the graph database design, traversal logic, blast radius calculations, and API queries running in the Lokii Platform.

## Overview
Lokii utilizes Neo4j to model cyber-range telemetry and map threat linkages. Unlike relational systems requiring complex joins, Neo4j traces paths between Users, Accounts, Transactions, Devices, and IPs in real-time, enabling the Investigation Agent to compute blast radius and identify missing evidence.

---

## Detailed Explanation

### 1. The Neo4j Node Schema
The Evidence Graph models entities as nodes and interactions as relationships:

| Node Label | Key Attributes | Description |
|------------|----------------|-------------|
| `User` | `id`, `username`, `email` | User identity matching core banking profiles |
| `Device` | `id`, `fingerprint`, `os` | User client endpoint fingerprints |
| `IP` | `address`, `asn`, `geo` | Network source IP addresses |
| `Account` | `id`, `currency`, `status` | Active banking accounts |
| `Transaction` | `id`, `amount`, `currency` | Core monetary transactions |

### 2. Relationships
- `(User)-[:USED_BY]->(Device)`: Device used by a specific identity.
- `(Device)-[:ASSOCIATED_WITH]->(IP)`: Device associated with a source IP.
- `(User)-[:OWNS]->(Account)`: Account ownership.
- `(Account)-[:CONTAINS]->(Transaction)`: Transaction associated with an account.

### 3. Traversal and Graph Queries
Graph traversal is implemented via Cypher queries:

#### Blast Radius Query
Calculates all entities connected to a compromised IP address up to a depth of 2 hops:
```cypher
MATCH (target:IP {address: "198.51.100.7"})-[r*1..2]-(connected)
RETURN connected.id, labels(connected) as type, count(r) as connections
```

#### Neighborhood Search Query
Retrieves immediate neighbor nodes for a specific device:
```cypher
MATCH (d:Device {id: "device-900"})-[r]-(neighbor)
RETURN type(r) as relation, neighbor.id, labels(neighbor) as type
```

### 4. How the Investigation Agent Consumes Graph Intelligence
During stateful execution, the LangGraph Agent invokes tool endpoints exposed by the Graph Service:
- **`GET /api/v1/graph/blast-radius/{node_id}`**: Evaluates the scope of compromise.
- **`POST /api/v1/graph/expand`**: Discovers neighbor nodes to expand the context.
- **`GET /api/v1/graph/investigation/{id}`**: Retrieves graph mappings for a specific case.

---

## Workflow

```
[Agent Node: graph_analysis]
             │
             ▼
[Call Graph Service Adapter] ──► (HTTP GET /api/v1/graph/blast-radius/user-42)
                                                 │
                                                 ▼
[Execute Cypher Traversal]   ◄── (Neo4j Graph Database Query)
             │
             ▼
[Update InvestigationState]
```

---

## Design Decisions
- **Loose Repository Coupling**: The system connects to database interfaces via an adapter layer. In local sandbox configurations, this defaults to an in-memory graph simulation to simplify setup.
- **Strict Read-Only Agent Access**: The Investigation Agent accesses graph data via read-only REST endpoints, preventing modification of evidence nodes.

## Best Practices
- **Max Depth Configuration**: Always set a depth limit (e.g. `*1..2` or `*1..3`) on Cypher path queries to prevent query timeout issues.
- **Tenancy Scoping**: Include a `tenant_id` check in all queries to ensure data partition safety.

## Future Enhancements
- Transition process-local memory configurations used in the MVP to database connections.
- Implement Cypher query caching to reduce Neo4j processor load.
