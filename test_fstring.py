# Test the f-string behavior
max_depth = 5
query = f'''
MATCH (source {{\$id: \$\$source_id, tenant_id: \$\$tenant_id}})
MATCH (target {{\$id: \$\$target_id, tenant_id: \$\$tenant_id}})
MATCH path = shortestPath((source)-[:*..{max_depth}]-(target))
RETURN nodes(path) as nodes
'''
print(repr(query))
print('---')
print(query)