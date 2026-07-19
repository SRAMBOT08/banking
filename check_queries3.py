with open(r'C:\Users\Lokesh Kumar\OneDrive\Desktop\Github\Cohort_Web_App\banking\investigation-service\app\graph\neo4j_repository.py', 'r') as f:
    content = f.read()

# Check the actual query strings
methods = ['create_node', 'update_node', 'merge_node', 'find_shortest_path', 'find_related_evidence', 'find_related_entities']

for method in methods:
    idx = content.find(f'async def {method}')
    if idx >= 0:
        q_idx = content.find('query =', idx)
        if q_idx >= 0:
            # Find the actual query
            start = content.find('"""', q_idx)
            if start >= 0:
                end = content.find('"""', start + 3)
                if end >= 0:
                    query = content[start:end+3]
                    print(f'{method}:')
                    print(query[:200])
                    print('---')