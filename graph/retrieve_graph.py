from graph.neo4j_client import Neo4jClient
from graph.extract_entity import extract_entity
from core.utils import normalize_entity

client = Neo4jClient()


def retrieve(query, k=2):
    # -------------------------------
    # STEP 1: Extract entity
    # -------------------------------
    entity, entity_type = extract_entity(query)

    entity_clean = normalize_entity(entity)
    entity_type = entity_type.lower()

    print(f"\n[DEBUG] Entity: {entity_clean}, Type: {entity_type}")



    cypher = """ 
    MATCH (n)
    WHERE (
        ($type = "disease" AND n:Disease) OR
        ($type = "symptom" AND n:Symptom) OR
        ($type = "drug" AND n:Drug) OR
        ($type = "treatment" AND n:Treatment) OR
        ($type = "riskfactor" AND n:RiskFactor) OR
        ($type = "paper" AND n:Paper) OR
        ($type = "biomarker" AND n:Biomarker)
    )

    WITH n,
         toLower(n.name) AS name,
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

    
    OPTIONAL MATCH (n)-[r]->(m)
    WHERE r.context IS NOT NULL

    OPTIONAL MATCH (x)-[r2]->(n)
    WHERE r2.context IS NOT NULL

    WITH score,
         collect(DISTINCT r.context) + collect(DISTINCT r2.context) AS contexts

    UNWIND contexts AS context

    RETURN context, score
    ORDER BY score DESC
    LIMIT $k
    """

    results = client.run_query(
        cypher,
        {"entity":entity_clean,"k":k,"type":entity_type}
    )
    print("[DEBUG] Raw Results:", results)

    docs = []
    for r in results:
        if r.get("context"):
            docs.append(r["context"].strip())
    if len(docs) == 0:
        print("[DEBUG] Fallback to type-agnostic search")

        cypher_fallback = """
        MATCH (n)
        WITH n,
             toLower(n.name) AS name,
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

        OPTIONAL MATCH (n)-[r]->(m)
        WHERE r.context IS NOT NULL

        OPTIONAL MATCH (x)-[r2]->(n)
        WHERE r2.context IS NOT NULL

        WITH score,
             collect(DISTINCT r.context) + collect(DISTINCT r2.context) AS contexts

        UNWIND contexts AS context

        RETURN context, score
        ORDER BY score DESC
        LIMIT $k
        """

        results = client.run_query(
            cypher_fallback,
            {"entity": entity_clean, "k": k}
        )
        docs = [r["context"].strip() for r in results if r.get("context")]

    return docs