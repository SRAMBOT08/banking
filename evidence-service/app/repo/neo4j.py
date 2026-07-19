"""Neo4j graph repository for evidence service."""
from __future__ import annotations

from typing import Any, Dict, List, Optional
from datetime import datetime
from datetime import timezone

from neo4j import AsyncGraphDatabase, AsyncDriver, AsyncSession
from neo4j.exceptions import Neo4jError

from app.repo.interfaces import GraphRepository
from app.config.settings import settings


class Neo4jGraphRepository(GraphRepository):
    """Neo4j implementation of the GraphRepository interface for evidence service."""

    def __init__(self, driver: Optional[AsyncDriver] = None):
        self._driver = driver
        self._initialized = False

    def _ensure_driver(self):
        """Lazy-initialize the driver."""
        if self._driver is None:
            self._driver = AsyncGraphDatabase.driver(
                "bolt://localhost:7687",
                auth=("neo4j", "testpassword"),
                max_connection_pool_size=50,
                connection_acquisition_timeout=30,
            )

    async def create_node(self, canonical_id: str, labels: List[str], properties: Dict[str, Any]):
        """Create a new node with the given labels and properties."""
        self._ensure_driver()
        async with AsyncGraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "testpassword")).session() as session:
            labels_str = ":".join(labels)
            query = f"""
            CREATE (n:{labels_str} {{
                canonical_id: $canonical_id,
                properties: $properties
            }})
            RETURN n
            """
            await session.run(query, canonical_id=canonical_id, properties=properties)

    async def merge_node(self, canonical_id: str, labels: List[str], properties: Dict[str, Any]):
        """Merge (upsert) a node with the given labels and properties."""
        self._ensure_driver()
        async with AsyncGraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "testpassword")).session() as session:
            labels_str = ":".join(labels)
            query = f"""
            MERGE (n:{labels_str} {{canonical_id: $canonical_id}})
            ON CREATE SET
                n.properties = $properties,
                n.created_at = datetime()
            ON MATCH SET
                n.properties = $properties,
                n.updated_at = datetime()
            RETURN n
            """
            await session.run(query, canonical_id=canonical_id, properties=properties)

    async def create_relationship(self, from_id: str, to_id: str, relationship_type: str, properties: Dict[str, Any]):
        """Create a relationship between two nodes."""
        self._ensure_driver()
        async with AsyncGraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "testpassword")).session() as session:
            query = f"""
            MATCH (from {{canonical_id: $from_id}})
            MATCH (to {{canonical_id: $to_id}})
            CREATE (from)-[:{relationship_type} $properties]->(to)
            RETURN from, to
            """
            await session.run(query, from_id=from_id, to_id=to_id, properties=properties)

    async def merge_relationship(self, from_id: str, to_id: str, relationship_type: str, properties: Dict[str, Any]):
        """Merge (upsert) a relationship between two nodes."""
        self._ensure_driver()
        async with AsyncGraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "testpassword")).session() as session:
            query = f"""
            MATCH (from {{canonical_id: $from_id}})
            MATCH (to {{canonical_id: $to_id}})
            MERGE (from)-[r:{relationship_type}]->(to)
            ON CREATE SET r.properties = $properties, r.created_at = datetime()
            ON MATCH SET r.properties = $properties, r.updated_at = datetime()
            RETURN from, to
            """
            await session.run(query, from_id=from_id, to_id=to_id, properties=properties)

    async def fetch_entity(self, canonical_id: str) -> Optional[Dict[str, Any]]:
        """Fetch an entity by its canonical ID."""
        async with AsyncGraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "testpassword")).session() as session:
            query = """
            MATCH (n {canonical_id: $canonical_id})
            RETURN n
            """
            result = await session.run(query, canonical_id=canonical_id)
            record = await result.single()
            if record:
                node = record["n"]
                return dict(node)
            return None

    async def close(self):
        """Close the driver connection."""
        pass


# Global instance
neo4j_graph_repo = Neo4jGraphRepository()