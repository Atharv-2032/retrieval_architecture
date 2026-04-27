from graph.neo4j_client import Neo4jClient
from graph.extract_entity import extract_entities
from graph.select_paths import select_traversal_paths
from core.utils import normalize_entity

client = Neo4jClient()


def retrieve(query, k=8):

    entities = extract_entities(query)
    print("\n[DEBUG] Entities:", entities)

    if not entities:
        print("[WARN] No entities extracted, skipping graph retrieval")
        return []

    paths = select_traversal_paths(query, entities)
    paths = list(set(paths + ["MENTIONS"]))
    print("\n[DEBUG] Paths:", paths)

    debug_cypher = """
    UNWIND $entities AS ent

    MATCH (a)
    WHERE a.name IS NOT NULL OR a.title IS NOT NULL

    WITH a, ent,
         toLower(coalesce(a.name, a.title)) AS name,
         ent.name AS entity

    WITH a, ent,
    CASE
        WHEN name = entity THEN 5
        WHEN name STARTS WITH entity THEN 4
        WHEN entity STARTS WITH name THEN 4
        WHEN name CONTAINS entity THEN 3
        WHEN entity CONTAINS name THEN 3
        ELSE 0
    END AS score

    WHERE score > 0

    WITH a, ent, score
    ORDER BY score DESC
    LIMIT 3

    RETURN coalesce(a.name, a.title) AS matched_node, labels(a) AS label, ent.name AS searched_for, score
    """

    matched = client.run_query(
        debug_cypher,
        {
            "entities": [{"name": normalize_entity(e["entity"]), "type": e["type"]} for e in entities],
            "paths": paths,
            "k": k
        }
    )

    print("\n[DEBUG] Matched Nodes:")
    for m in matched:
        print(f"  searched_for='{m['searched_for']}' → matched='{m['matched_node']}' ({m['label']}) score={m['score']}")

    cypher = """
    UNWIND $entities AS ent

    MATCH (a)
    WHERE a.name IS NOT NULL OR a.title IS NOT NULL

    WITH a, ent,
         toLower(coalesce(a.name, a.title)) AS name,
         ent.name AS entity

    WITH a, ent,
    CASE
        WHEN name = entity THEN 5
        WHEN name STARTS WITH entity THEN 4
        WHEN entity STARTS WITH name THEN 4
        WHEN name CONTAINS entity THEN 3
        WHEN entity CONTAINS name THEN 3
        ELSE 0
    END AS score

    WHERE score > 0

    WITH a, ent, score
    ORDER BY score DESC
    LIMIT 3

    OPTIONAL MATCH (a)-[r1]->(b)
    WHERE (toLower(coalesce(b.name, b.title)) CONTAINS ent.name
       OR ent.name CONTAINS toLower(coalesce(b.name, b.title)))
      AND type(r1) IN $paths
      AND r1.context IS NOT NULL

    OPTIONAL MATCH (a)-[r2]->(x)
    WHERE type(r2) IN $paths
      AND r2.context IS NOT NULL

    OPTIONAL MATCH (y)-[r3]->(a)
    WHERE type(r3) IN $paths
      AND r3.context IS NOT NULL

    WITH a, score,
         collect(DISTINCT r1.context) AS c1,
         collect(DISTINCT r2.context) AS c2,
         collect(DISTINCT r3.context) AS c3

    WITH score,
         [c IN c1 + c2 + c3 WHERE c IS NOT NULL] AS all_contexts

    UNWIND all_contexts AS context
    RETURN DISTINCT context, score
    ORDER BY score DESC
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