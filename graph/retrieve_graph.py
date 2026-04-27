from graph.neo4j_client import Neo4jClient
from graph.extract_entity import extract_entities
from graph.select_paths import select_traversal_paths
from core.utils import normalize_entity

client = Neo4jClient()

def retrieve(query, k=8):

    entities = extract_entities(query)
    print("\n[DEBUG] Entities:", entities)

    paths = select_traversal_paths(query, entities)
    print("\n[DEBUG] Paths:", paths)

    cypher = """
    UNWIND $entities AS ent

    MATCH (a)
    WHERE toLower(a.name) CONTAINS ent.name
       OR ent.name CONTAINS toLower(a.name)

    OPTIONAL MATCH (a)-[r1]->(b)
    WHERE (toLower(b.name) CONTAINS ent.name
       OR ent.name CONTAINS toLower(b.name))
      AND type(r1) IN $paths
      AND r1.context IS NOT NULL

    OPTIONAL MATCH (a)-[r2]->(x)
    WHERE type(r2) IN $paths
      AND r2.context IS NOT NULL

    OPTIONAL MATCH (y)-[r3]->(a)
    WHERE type(r3) IN $paths
      AND r3.context IS NOT NULL

    WITH a,
         collect(DISTINCT r1.context) AS c1,
         collect(DISTINCT r2.context) AS c2,
         collect(DISTINCT r3.context) AS c3

    WITH [c IN c1 + c2 + c3 WHERE c IS NOT NULL] AS all_contexts

    UNWIND all_contexts AS context
    RETURN DISTINCT context
    LIMIT $k
    """

    results = client.run_query(
        cypher,
        {
            "entities": [{"name": normalize_entity(e["entity"]), "type": e["type"]} for e in entities],
            "paths": paths,
            "k": k
        }
    )

    print("[DEBUG] Raw Results:", results)

    docs = list(dict.fromkeys(
        r["context"].strip()
        for r in results
        if r.get("context")
    ))

    return docs[:k]