from neo4j import GraphDatabase
driver = GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j', 'testpassword'))
with driver.session() as session:
    result = session.run('SHOW CONSTRAINTS')
    constraints = [dict(r) for r in result]
    print('=== CONSTRAINTS ===')
    for c in constraints:
        print(f"  {c['name']}: {c['type']} on {c['labelsOrTypes']}.{c['properties']}")
    
    result = session.run('SHOW INDEXES')
    indexes = [dict(r) for r in result]
    print('\n=== INDEXES ===')
    for i in indexes:
        if i['type'] == 'RANGE':
            print(f"  {i['name']}: {i['type']} on {i['labelsOrTypes']}.{i['properties']}")
driver.close()