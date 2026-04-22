from graph.neo4j_client import Neo4jClient
from core.utils import normalize_entity
client = Neo4jClient()


def match_entities(entities,limit_per_entity = 2):
    entities = entities[:5]
    matched_nodes = []
    for entity in entities:
        entity_lower = entity.lower()
        entity_clean = normalize_entity(entity_lower)

        cypher = """
                    MATCH (n)
                    WITH n,
                    toLower(coalesce(n.name, n.title)) AS name,
                    $entity AS entity

                    WITH n, name, entity,
                    CASE 
                        WHEN name = entity THEN 3
                        WHEN name STARTS WITH entity THEN 2
                        WHEN name CONTAINS entity THEN 1
                        WHEN entity CONTAINS name THEN 2   
                        ELSE 0
                    END AS score

                    WHERE score > 0

                    RETURN 
                        labels(n) AS labels,
                        name AS value,
                        score
                    ORDER BY score DESC
                    LIMIT $limit
                    """
        result = client.run_query(
            cypher,
            {"entity":entity_clean,"limit":limit_per_entity}

        )
        print(f"\n[DEBUG] Matches for '{entity}': {result}")

        for r in result:
            matched_nodes.append({
                "entities":entity,
                "label": r.get("labels",[]),
                "values":r.get("value",""),
                "score" : r.get("score",0)
            })
    return matched_nodes
