with open(r'C:\Users\Lokesh Kumar\OneDrive\Desktop\Github\Cohort_Web_App\banking\investigation-service\app\graph\neo4j_repository.py', 'r') as f:
    content = f.read()

# Fix: change rf""" back to f""" for queries that have interpolation
# But keep rf""" for queries without interpolation

# The queries with interpolation are:
# 1. create_node (has type-specific clauses)
# 2. update_node (has type-specific clauses)
# 3. merge_node (has type-specific clauses)
# 4. find_shortest_path (has {max_depth})
# 5. find_related_evidence (has {depth})
# 6. find_related_entities (has {max_depth})

# The queries WITHOUT interpolation (can stay rf):
# 1. get_node
# 2. delete_node
# 3. create_relationship
# 4. get_relationships
# 5. get_neighbors
# 7. search_nodes
# 8. execute_custom_query
# 9. health_check
# 10. create_constraints_and_indexes
# 11. find_related_entities (has {max_depth})

# Actually, find_related_entities has {max_depth} so it needs f"""
# Let me check which ones have {...} interpolation

# Let's do targeted fixes:
# Change rf""" to f""" for specific methods

# First, let's see the current state of each query
methods_with_interpolation = [
    'create_node',
    'update_node', 
    'merge_node',
    'find_shortest_path',
    'find_related_evidence',
    'find_related_entities',
]

for method in methods_with_interpolation:
    # Find the query in this method
    idx = content.find(f'async def {method}')
    if idx >= 0:
        # Find the query = 
        q_idx = content.find('query =', idx)
        if q_idx >= 0:
            # Check if it's rf or f
            context = content[max(0,q_idx-20):q_idx+10]
            print(f'{method}: {context}')

print('---')

# Now let's check the actual query strings to see if they have interpolation
for method in methods_with_interpolation:
    idx = content.find(f'async def {method}')
    if idx >= 0:
        q_idx = content.find('query =', idx)
        if q_idx >= 0:
            q_end = content.find('"""', q_idx + 10)
            if q_end > 0:
                query_text = content[q_idx:q_end+3]
                # Check for interpolation markers
                has_interpolation = '{' in query_text and '}' in query_text
                is_raw = 'rf"""' in content[max(0,q_idx-10):q_idx]
                print(f'{method}: raw={is_raw}, has_interpolation={has_interpolation}')
                if has_interpolation and is_raw:
                    print(f'  NEEDS FIX: {method} has interpolation but is raw!')