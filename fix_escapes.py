import re

with open(r'C:\Users\Lokesh Kumar\OneDrive\Desktop\Github\Cohort_Web_App\banking\investigation-service\app\graph\neo4j_repository.py', 'r') as f:
    content = f.read()

# In f-strings, we need to escape $ as $$
# Fix the query strings - replace \$ with $$ for all query parameters
# This is a more targeted fix

# Fix find_shortest_path
content = content.replace('MATCH (source {{id: \$source_id, tenant_id: \$tenant_id}})', 'MATCH (source {{id: $$source_id, tenant_id: $$tenant_id}})')
content = content.replace('MATCH (target {{id: \$target_id, tenant_id: \$tenant_id}})', 'MATCH (target {{id: $$target_id, tenant_id: $$tenant_id}})')
content = content.replace('MATCH (inv {{id: \$investigation_id, tenant_id: \$tenant_id}})', 'MATCH (inv {{id: $$investigation_id, tenant_id: $$tenant_id}})')
content = content.replace('MATCH (e {{id: \$entity_id, tenant_id: \$tenant_id}})', 'MATCH (e {{id: $$entity_id, tenant_id: $$tenant_id}})')
content = content.replace('WHERE related.tenant_id = \$tenant_id', 'WHERE related.tenant_id = $$tenant_id')

# Also fix the f-string query strings where parameters are used
content = content.replace('\$source_id', '$$source_id')
content = content.replace('\$target_id', '$$target_id')
content = content.replace('\$tenant_id', '$$tenant_id')
content = content.replace('\$investigation_id', '$$investigation_id')
content = content.replace('\$entity_id', '$$entity_id')

with open(r'C:\Users\Lokesh Kumar\OneDrive\Desktop\Github\Cohort_Web_App\banking\investigation-service\app\graph\neo4j_repository.py', 'w') as f:
    f.write(content)

print('Done')