with open(r'C:\Users\Lokesh Kumar\OneDrive\Desktop\Github\Cohort_Web_App\banking\investigation-service\app\graph\neo4j_repository.py', 'r') as f:
    content = f.read()

# The issue: in the source code, we have \$ which becomes backslash-dollar in the string
# We need to replace \$ with $ in the query strings
# But we must be careful - only in the Cypher query parts, not in Python code

# The pattern: in rf-strings, \$ should be just $
# But in Python code like f"{key}: \${key}", we also need to fix

# Let's do a simple replacement: replace all \$ with $ in the entire file
# This should be safe because \$ doesn't appear in valid Python code otherwise
content = content.replace('\\$', '$')

with open(r'C:\Users\Lokesh Kumar\OneDrive\Desktop\Github\Cohort_Web_App\banking\investigation-service\app\graph\neo4j_repository.py', 'w') as f:
    f.write(content)

print('Fixed all \\$ to $')