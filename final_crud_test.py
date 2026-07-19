import asyncio
import sys
sys.path.append(r'C:\Users\Lokesh Kumar\OneDrive\Desktop\Github\Cohort_Web_App\banking\investigation-service')

from app.graph.neo4j_repository import Neo4jGraphRepository
from app.graph.client import graph_manager
from app.graph.models import (
    EntityNode, EvidenceNode, NodeType, GraphRelationship, RelationshipType
)
from datetime import datetime, timezone

async def test():
    await graph_manager.initialize()
    repo = Neo4jGraphRepository()
    
    tenant_id = 'tenant-unique-final'
    
    # Test create_node
    node = EntityNode(id='node-1', type=NodeType.ENTITY, tenant_id=tenant_id, name='Test Node', confidence=0.8)
    created = await repo.create_node(node)
    print(f'create_node: {created.id}, name={created.name}')
    
    # Test get_node
    retrieved = await repo.get_node('node-1', tenant_id)
    print(f'get_node: {retrieved.id}, name={retrieved.name}')
    
    # Test update_node
    retrieved.name = 'Updated Name'
    retrieved.confidence = 0.9
    updated = await repo.update_node(retrieved)
    print(f'update_node: {updated.id}, name={updated.name}, confidence={updated.confidence}')
    
    # Test merge_node idempotency
    node2 = EntityNode(id='node-1', type=NodeType.ENTITY, tenant_id=tenant_id, name='Should Not Change', confidence=0.5)
    merged = await repo.merge_node(node2)
    print(f'merge_node: {merged.id}, name={merged.name}')
    
    # Test create_relationship
    node_a = EntityNode(id='a', type=NodeType.ENTITY, tenant_id=tenant_id, name='A')
    node_b = EntityNode(id='b', type=NodeType.ENTITY, tenant_id=tenant_id, name='B')
    await repo.merge_node(node_a)
    await repo.merge_node(node_b)
    
    rel = GraphRelationship(source_id='a', target_id='b', type=RelationshipType.RELATED_TO, tenant_id=tenant_id, metadata={'test': 'meta'}, created_at=datetime.now(timezone.utc))
    created_rel = await repo.create_relationship(rel)
    print(f'create_relationship: {created_rel.source_id} -> {created_rel.target_id}')
    
    # Test get_relationships
    relationships = await repo.get_relationships('a', tenant_id)
    print(f'get_relationships: {len(relationships)} relationships')
    
    # Test get_neighbors
    neighbors = await repo.get_neighbors('a', tenant_id)
    print(f'get_neighbors: {len(neighbors)} neighbors')
    
    # Test find_shortest_path
    node_c = EntityNode(id='c', type=NodeType.ENTITY, tenant_id=tenant_id, name='C')
    await repo.merge_node(node_c)
    rel_bc = GraphRelationship(source_id='b', target_id='c', type=RelationshipType.RELATED_TO, tenant_id=tenant_id, metadata={}, created_at=datetime.now(timezone.utc))
    await repo.merge_relationship(rel_bc)
    
    path = await repo.find_shortest_path('a', 'c', tenant_id, max_depth=5)
    print(f'find_shortest_path: {len(path)} nodes')
    for p in path:
        print(f'  - {p.id}')
    
    # Test search_nodes
    results = await repo.search_nodes(tenant_id, node_type='Entity', limit=10)
    print(f'search_nodes: {len(results)} results')
    
    # Test find_related_evidence
    evidence = EvidenceNode(id='ev-1', type=NodeType.EVIDENCE, tenant_id=tenant_id, evidence_type='test', source='test', confidence=1.0, timestamp=datetime.now(timezone.utc))
    await repo.merge_node(evidence)
    rel_ev = GraphRelationship(source_id='ev-1', target_id='a', type=RelationshipType.OBSERVED_ON, tenant_id=tenant_id, metadata={}, created_at=datetime.now(timezone.utc))
    await repo.merge_relationship(rel_ev)
    
    related_ev = await repo.find_related_evidence('a', tenant_id, depth=2)
    print(f'find_related_evidence: {len(related_ev)} results')
    
    # Test find_related_entities
    related_ent = await repo.find_related_entities('a', tenant_id, max_depth=2)
    print(f'find_related_entities: {len(related_ent)} results')
    
    # Test execute_custom_query - use $tenant directly (no backslash)
    custom = await repo.execute_custom_query('MATCH (n) WHERE n.tenant_id = $tenant RETURN count(n) as count', {'tenant': tenant_id})
    print(f'execute_custom_query: {custom}')
    
    # Test health_check
    healthy = await repo.health_check()
    print(f'health_check: {healthy}')
    
    # Test delete_node
    deleted = await repo.delete_node('node-1', tenant_id)
    print(f'delete_node: {deleted}')
    
    # Verify deletion
    retrieved = await repo.get_node('node-1', tenant_id)
    print(f'After delete get_node: {retrieved}')
    
    await graph_manager.close()

asyncio.run(test())