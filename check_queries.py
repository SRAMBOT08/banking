with open(r'C:\Users\Lokesh Kumar\OneDrive\Desktop\Github\Cohort_Web_App\banking\investigation-service\app\graph\neo4j_repository.py', 'r') as f:
    content = f.read()

# Find find_related_evidence query
idx = content.find('find_related_evidence')
if idx > 0:
    query_start = content.find('query =', idx)
    query_end = content.find('"""', query_start + 10)
    if query_end > 0:
        print('Found query:')
        print(content[query_start:query_end+3])
    else:
        print("Could not find end of query")

# Also check find_related_entities
idx2 = content.find('find_related_entities')
if idx2 > 0:
    query_start2 = content.find('query =', idx2)
    query_end2 = content.find('"""', query_start2 + 10)
    if query_end2 > 0:
        print('Found query 2:')
        print(content[query_start2:query_end2+3])