# Fix the backslash-dollar in query strings
with open(r'C:\Users\Lokesh Kumar\OneDrive\Desktop\Github\Cohort_Web_App\banking\investigation-service\app\graph\neo4j_repository.py', 'r') as f:
    content = f.read()

# In the source code, the queries have literal backslash-dollar (\$) 
# which becomes backslash-dollar in the string. We need just dollar ($)
# The pattern in source: '\\\$' represents literal backslash-dollar in string
# We need to replace with just '$'

# In the Python source file, the literal backslash-dollar appears as '\\\\$'
# (four chars: backslash, backslash, backslash, dollar)
# We want to replace with just '$' (one char)

content = content.replace('\\\\\\$', '$')

with open(r'C:\Users\Lokesh Kumar\OneDrive\Desktop\Github\Cohort_Web_App\banking\investigation-service\app\graph\neo4j_repository.py', 'w') as f:
    f.write(content)

print('Fixed backslash-dollar')