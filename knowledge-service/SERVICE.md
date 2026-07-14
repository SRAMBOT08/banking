Knowledge Service Contract

Responsibility:
- Maintain Attack Knowledge Graph, import MITRE ATT&CK mappings and banking fraud ontology.

Inputs:
- knowledge.imports (manual/admin)

Outputs:
- knowledge.graph.updated.v1

Kafka Topics Produced:
- knowledge.graph.updated.v1

Kafka Topics Consumed:
- admin.knowledge.imports

Database Ownership:
- Attack Knowledge Graph (Neo4j)

External Integrations:
- Knowledge sources (MITRE datasets)

Dependencies:
- shared library

Shared Models Used:
- shared.models.knowledge.*
