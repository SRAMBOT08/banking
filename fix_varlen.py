with open(r'C:\Users\Lokesh Kumar\OneDrive\Desktop\Github\Cohort_Web_App\banking\investigation-service\app\graph\neo4j_repository.py', 'r') as f:
    content = f.read()

# Fix the variable-length relationship syntax
# Change [:*1..{depth}] to [*1..{depth}] (remove the colon)
# Change [:*1..{max_depth}] to [*1..{max_depth}]

content = content.replace('[:*{', '[*{')
content = content.replace(':*1..', '*1..')

with open(r'C:\Users\Lokesh Kumar\OneDrive\Desktop\Github\Cohort_Web_App\banking\investigation-service\app\graph\neo4j_repository.py', 'w') as f:
    f.write(content)

print('Fixed variable-length relationship syntax')