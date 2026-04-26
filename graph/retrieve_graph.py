from graph.neo4j_client import Neo4jClient
from graph.extract_entity import extract_entities
from graph.select_paths import select_traversal_paths
from core.utils import normalize_entity

client = Neo4jClient()


def retrieve(query, k=8):

   
    entities = extract_entities(query)
    print("\n[DEBUG] Entities:", entities)

    entity_values = [normalize_entity(e["entity"]) for e in entities]

    
    paths = select_traversal_paths(query, entities)
    print("\n[DEBUG] Paths:", paths)

   
    cypher = """
    MATCH (a)
    WHERE ANY(e IN $entities WHERE toLower(a.name) CONTAINS e)

    
    OPTIONAL MATCH (a)-[r]->(b)
    WHERE ANY(e IN $entities WHERE toLower(b.name) CONTAINS e)
      AND type(r) IN $paths
      AND r.context IS NOT NULL

   
    OPTIONAL MATCH (a)-[r2]->(x)
    WHERE type(r2) IN $paths
      AND r2.context IS NOT NULL

    
    OPTIONAL MATCH (y)-[r3]->(a)
    WHERE type(r3) IN $paths
      AND r3.context IS NOT NULL

    WITH 
        collect(DISTINCT r.context) +
        collect(DISTINCT r2.context) +
        collect(DISTINCT r3.context) AS contexts

    UNWIND contexts AS context

    RETURN context
    LIMIT $k
    """

    results = client.run_query(
        cypher,
        {
            "entities": entity_values,
            "paths": paths,
            "k": k
        }
    )

    print("[DEBUG] Raw Results:", results)

    docs = [r["context"].strip() for r in results if r.get("context")]

    return docs