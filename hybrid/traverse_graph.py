from graph.neo4j_client import Neo4jClient
from core.utils import normalize_entity

client = Neo4jClient()

def traverse_graph(matched_nodes, paths, k=2):
    if not matched_nodes or not paths:
        return []

    results = []

    for node in matched_nodes:
        entity_clean = normalize_entity(node["values"])

        cypher = """
        
                 MATCH (n)
        WHERE n.name IS NOT NULL OR n.title IS NOT NULL

        WITH n,
             toLower(coalesce(n.name, n.title)) AS name,
             $entity AS entity

        WITH n, name, entity,
        CASE 
            WHEN name = entity THEN 5
            WHEN name STARTS WITH entity THEN 4
            WHEN entity STARTS WITH name THEN 4
            WHEN name CONTAINS entity THEN 3
            WHEN entity CONTAINS name THEN 3
            ELSE 0
        END AS score

        WHERE score > 0

        WITH n, score
        ORDER BY score DESC
        LIMIT $k

        OPTIONAL MATCH (n)-[r]->(x)
        WHERE type(r) IN $paths AND r.context IS NOT NULL


        OPTIONAL MATCH (y)-[r2]->(n)
        WHERE type(r2) IN $paths AND r2.context IS NOT NULL

        WITH 
            score,
            collect(DISTINCT r.context) + collect(DISTINCT r2.context) AS contexts

        UNWIND contexts AS context

        RETURN context, score
        ORDER BY score DESC
        LIMIT $k

        """

        query_results = client.run_query(
            cypher,
            {"entity": entity_clean, "k": k, "paths": paths}
        )

        print(f"\n[DEBUG] Traversal for '{entity_clean}':", query_results)

        results.extend(query_results)

    return results