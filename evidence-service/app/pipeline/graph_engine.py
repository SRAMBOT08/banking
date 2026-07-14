from __future__ import annotations

from typing import Dict, Any

from app.core.logger import get_logger
from app.repo.interfaces import GraphRepository

logger = get_logger("graph_engine")


class GraphEngine:
    def __init__(self, repo: GraphRepository):
        self.repo = repo

    def apply(self, resolved_entities: Dict[str, list], relationships: list):
        # create/merge nodes
        for etype, items in resolved_entities.items():
            for it in items:
                cid = it["canonical_id"]
                props = it.get("attributes", {})
                labels = [etype.upper()]
                self.repo.merge_node(cid, labels, props)

        # create/merge relationships
        for r in relationships:
            self.repo.merge_relationship(r["from"], r["to"], r["type"], {})

        logger.info("graph_apply_complete", extra={"nodes": len(self.repo.nodes), "rels": len(self.repo.relationships)})
