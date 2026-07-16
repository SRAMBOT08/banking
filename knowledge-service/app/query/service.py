from __future__ import annotations
import logging
from typing import Optional
from .models import *
from .repository import KnowledgeRepository

logger = logging.getLogger("sentineliq.knowledge.query")


class KnowledgeQueryService:
    """Read-only application service; all knowledge decisions remain in providers."""
    def __init__(self, repository: KnowledgeRepository):
        self._repository = repository

    def _log(self, operation: str, **fields):
        logger.info({"event": "knowledge_query", "operation": operation, **fields})

    def find_item(self, item_id: str): self._log("find_item", item_id=item_id); return self._repository.find_item(item_id)
    def find_pattern(self, item_id: str): self._log("find_pattern", item_id=item_id); return self._repository.find_pattern(item_id)
    def find_technique(self, item_id: str): self._log("find_technique", item_id=item_id); return self._repository.find_technique(item_id)
    def find_tactic(self, item_id: str): self._log("find_tactic", item_id=item_id); return self._repository.find_tactic(item_id)
    def find_control(self, item_id: str): self._log("find_control", item_id=item_id); return self._repository.find_control(item_id)
    def find_recommendation(self, item_id: str): self._log("find_recommendation", item_id=item_id); return self._repository.find_recommendation(item_id)
    def find_playbook(self, item_id: str): self._log("find_playbook", item_id=item_id); return self._repository.find_playbook(item_id)
    def find_fraud_pattern(self, item_id: str): self._log("find_fraud_pattern", item_id=item_id); return self._repository.find_fraud_pattern(item_id)
    def find_detection_rule(self, item_id: str): self._log("find_detection_rule", item_id=item_id); return self._repository.find_detection_rule(item_id)
    def find_indicator(self, item_id: str): self._log("find_indicator", item_id=item_id); return self._repository.find_indicator(item_id)
    def find_quantum_pattern(self, item_id: str): self._log("find_quantum_pattern", item_id=item_id); return self._repository.find_quantum_pattern(item_id)
    def find_relationship(self, relationship_id: str): self._log("find_relationship", relationship_id=relationship_id); return self._repository.find_relationship(relationship_id)
    def relationships(self, item_id: str): self._log("relationships", item_id=item_id); return self._repository.relationships(item_id)
    def search(self, request: KnowledgeSearchRequest): self._log("search", query=request.query, category=request.category); return self._repository.search(request)
    def metadata(self): self._log("metadata"); return self._repository.metadata()
    def statistics(self): self._log("statistics"); return self._repository.statistics()
    def validate(self): self._log("validate"); return self._repository.validate()
    def versions(self, item_id: str): self._log("versions", item_id=item_id); return self._repository.versions(item_id)
    def similar(self, item_id: str, limit: int = 10): self._log("similar", item_id=item_id); return self._repository.similar(item_id, limit)
