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

                WITH n
                ORDER BY score DESC
                LIMIT $k

                OPTIONAL MATCH (n)-[r]->(x)
                WHERE type(r) IN $paths

                OPTIONAL MATCH (x)-[r2]->(y)
                WHERE type(r2) IN $paths

                OPTIONAL MATCH (p:Paper)-[:MENTIONS]->(n)

                RETURN 
                    coalesce(n.name, n.title) AS entity,
                    collect(DISTINCT x.name) AS related_entities,
                    collect(DISTINCT y.name) AS second_hop,
                    collect(DISTINCT p.title) AS papers,
                    collect(DISTINCT type(r)) AS used_relations

        """

        query_results = client.run_query(
            cypher,
            {"entity": entity_clean, "k": k, "paths": paths}
        )

        print(f"\n[DEBUG] Traversal for '{entity_clean}':", query_results)

        results.extend(query_results)

    return results