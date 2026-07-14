Evidence Intelligence Service Contract

Responsibility:
- Entity extraction, resolution, correlation, evidence graph construction and persistence to Neo4j.

Inputs:
- events.unified.v1

Outputs:
- evidence.graph.events.v1 (graph update events)

Kafka Topics Produced:
- evidence.graph.events.v1

Kafka Topics Consumed:
- events.unified.v1

Database Ownership:
- Evidence Graph (Neo4j)

External Integrations:
- Neo4j

Dependencies:
- shared library

Shared Models Used:
- shared.models.graph.*
