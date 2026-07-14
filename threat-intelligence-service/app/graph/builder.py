from __future__ import annotations
from typing import Dict, Any
from app.repositories.inmemory_attack_graph import InMemoryAttackGraphRepository
from app.core.logger import get_logger

logger = get_logger("graph_builder")


def build_attack_graph(repo: InMemoryAttackGraphRepository, patterns: Dict[str, Dict]):
    # Patterns already contain nodes & edges; delegate to repo
    repo.load_patterns(patterns)
    logger.info("attack_graph_built", extra={"patterns": len(patterns)})
    return repo
