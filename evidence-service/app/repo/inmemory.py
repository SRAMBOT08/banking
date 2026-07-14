from __future__ import annotations

from typing import Dict, Any, List, Optional
from app.repo.interfaces import GraphRepository
from app.core.logger import get_logger

logger = get_logger("inmemory_repo")


class InMemoryGraphRepo(GraphRepository):
    def __init__(self):
        self.nodes: Dict[str, Dict[str, Any]] = {}
        self.relationships: List[Dict[str, Any]] = []

    def create_node(self, canonical_id: str, labels: List[str], properties: Dict[str, Any]):
        if canonical_id in self.nodes:
            raise ValueError("node_exists")
        self.nodes[canonical_id] = {"labels": labels, "properties": properties}
        logger.info("node_created", extra={"id": canonical_id})

    def merge_node(self, canonical_id: str, labels: List[str], properties: Dict[str, Any]):
        node = self.nodes.get(canonical_id, {"labels": labels, "properties": {}})
        node["properties"].update(properties)
        node["labels"] = list(set(node.get("labels", []) + labels))
        self.nodes[canonical_id] = node
        logger.info("node_merged", extra={"id": canonical_id})

    def create_relationship(self, from_id: str, to_id: str, rel_type: str, properties: Dict[str, Any]):
        self.relationships.append({"from": from_id, "to": to_id, "type": rel_type, "properties": properties})
        logger.info("relationship_created", extra={"from": from_id, "to": to_id, "type": rel_type})

    def merge_relationship(self, from_id: str, to_id: str, rel_type: str, properties: Dict[str, Any]):
        for r in self.relationships:
            if r["from"] == from_id and r["to"] == to_id and r["type"] == rel_type:
                r["properties"].update(properties)
                logger.info("relationship_merged", extra={"from": from_id, "to": to_id, "type": rel_type})
                return
        self.create_relationship(from_id, to_id, rel_type, properties)

    def fetch_entity(self, canonical_id: str) -> Optional[Dict[str, Any]]:
        return self.nodes.get(canonical_id)
