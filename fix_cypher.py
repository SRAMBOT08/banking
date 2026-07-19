with open(r'C:\Users\Lokesh Kumar\OneDrive\Desktop\Github\Cohort_Web_App\banking\investigation-service\app\graph\neo4j_repository.py', 'r') as f:
    content = f.read()

# Fix the MERGE query - change {$id: $id to {id: $id
content = content.replace('{$id: $id, tenant_id: $tenant_id}', '{id: $id, tenant_id: $tenant_id}')

# Fix other similar patterns
import re
# Find all patterns like {$key: $value} and fix them
content = re.sub(r'\{\$(\w+): \$(\w+)', r'{\1: $\2', content)

with open(r'C:\Users\Lokesh Kumar\OneDrive\Desktop\Github\Cohort_Web_App\banking\investigation-service\app\graph\neo4j_repository.py', 'w') as f:
    f.write(content)

print('Fixed')