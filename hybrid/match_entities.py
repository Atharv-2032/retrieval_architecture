from graph.neo4j_client import Neo4jClient
from core.utils import normalize_entity

client = Neo4jClient()

def match_entities(entities, limit_per_entity=2):
    entities = entities[:5]
    matched_nodes = []

    for entity in entities:
        entity_clean = normalize_entity(entity)

        cypher = """
        MATCH (n)
        WHERE coalesce(n.name, n.title) IS NOT NULL

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

        RETURN 
            labels(n) AS labels,
            coalesce(n.name, n.title) AS value,
            score
        ORDER BY score DESC
        LIMIT $limit
        """

        result = client.run_query(
            cypher,
            {"entity": entity_clean, "limit": limit_per_entity}
        )

        print(f"\n[DEBUG] Matches for '{entity}': {result}")

        for r in result:
            matched_nodes.append({
                "entities": entity,
                "label": r.get("labels", []),
                "values": r.get("value", ""),
                "score": r.get("score", 0)
            })

    return matched_nodes