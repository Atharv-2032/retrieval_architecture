from graph.neo4j_client import Neo4jClient

client = Neo4jClient()


def match_entities(entities,limit_per_entity = 2):
    entities = entities[:5]
    matched_nodes = []
    for entity in entities:
        keywords = entity.lower().split()
        cypher = """
        MATCH (n)
        WHERE ANY(word IN $keywords WHERE 
            toLower(coalesce(n.name, n.title)) CONTAINS word)

        RETURN 
            labels(n) AS labels,
            coalesce(n.name, n.title) AS value
        LIMIT $limit
        """
        result = client.run_query(
            cypher,
            {"keywords":keywords,"limit":limit_per_entity}

        )
        print(f"\n[DEBUG] Matches for '{entity}': {result}")

        for r in result:
            matched_nodes.append({
                "entities":entity,
                "label": r.get("labels",[]),
                "values":r.get("value","")
            })
    return matched_nodes
