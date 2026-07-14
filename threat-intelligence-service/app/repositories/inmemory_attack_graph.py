from __future__ import annotations
from typing import Dict, Any, List, Optional
import networkx as nx
from app.repositories.attack_graph_repository import AttackGraphRepository
from app.core.logger import get_logger

logger = get_logger("inmemory_attack_graph")


class InMemoryAttackGraphRepository(AttackGraphRepository):
    def __init__(self):
        self.graph = nx.DiGraph()
        self.pattern_index: Dict[str, Dict] = {}

    def load_patterns(self, patterns: Dict[str, Dict]):
        for name, p in patterns.items():
            if hasattr(p, "model_dump"):
                p = p.model_dump()
            # patterns define nodes and edges
            self.pattern_index[name] = p
            nodes = p.get('nodes', [])
            for n in nodes:
                nid = n.get('id') or f"{name}:{n.get('name')}"
                self.graph.add_node(nid, **n)
            for e in p.get('edges', []):
                self.graph.add_edge(e['from'], e['to'], **e)
        logger.info("patterns_loaded", extra={"count": len(patterns)})

    def get_pattern(self, name: str) -> Optional[Dict]:
        return self.pattern_index.get(name)

    def get_node(self, node_id: str) -> Optional[Dict]:
        if node_id in self.graph.nodes:
            return dict(self.graph.nodes[node_id])
        return None

    def find_by_mitre(self, technique: str) -> List[Dict]:
        out = []
        for name, p in self.pattern_index.items():
            if p.get('mitre', {}).get('technique') == technique:
                out.append(p)
        return out

    def traverse(self, start_nodes: List[str], depth: int = 3) -> Dict:
        # simple BFS traversal
        visited = set()
        edges = []
        for s in start_nodes:
            if s not in self.graph:
                continue
            for target in nx.single_source_shortest_path_length(self.graph, s, cutoff=depth):
                visited.add(target)
        for u, v, data in self.graph.edges(data=True):
            if u in visited and v in visited:
                edges.append({'from': u, 'to': v, **data})
        nodes = {n: dict(self.graph.nodes[n]) for n in visited}
        return {'nodes': nodes, 'edges': edges}
