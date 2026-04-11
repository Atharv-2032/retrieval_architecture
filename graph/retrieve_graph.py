from graph.neo4j_client import Neo4jClient
from graph.extract_entity import extract_entity

client = Neo4jClient()


def retrieve(query, k=5):
    # -------------------------------
    # STEP 1: Extract entity
    # -------------------------------
    entity, entity_type = extract_entity(query)

    entity = entity.lower()
    entity_type = entity_type.lower()

    keywords = entity.split()

    print(f"\n[DEBUG] Entity: {entity}, Type: {entity_type}")
    print(f"[DEBUG] Keywords: {keywords}")

    # -------------------------------
    # STEP 2: Choose simple query
    # -------------------------------

    if entity_type == "disease":
        cypher = """
                MATCH (d:Disease)
        WHERE ANY(word IN $keywords WHERE toLower(d.name) CONTAINS word)

        OPTIONAL MATCH (d)-[:ASSOCIATED_WITH]->(s:Symptom)
        OPTIONAL MATCH (d)<-[:TREATS]-(dr:Drug)
        OPTIONAL MATCH (t:Treatment)-[:TREATS]->(d)
        OPTIONAL MATCH (p:Paper)-[:MENTIONS]->(d)

        RETURN 
            d.name AS disease,
            collect(DISTINCT s.name) AS symptoms,
            collect(DISTINCT dr.name) AS drugs,
            collect(DISTINCT t.name) AS treatments,
            collect(DISTINCT p.title) AS papers
        LIMIT $k
        """

    elif entity_type == "symptom":
        cypher = """
                MATCH (s:Symptom)
        WHERE ANY(word IN $keywords WHERE toLower(s.name) CONTAINS word)

        MATCH (d:Disease)-[:ASSOCIATED_WITH]->(s)
        OPTIONAL MATCH (d)<-[:TREATS]-(dr:Drug)
        OPTIONAL MATCH (t:Treatment)-[:TREATS]->(d)
        OPTIONAL MATCH (p:Paper)-[:MENTIONS]->(d)

        RETURN 
            d.name AS disease,
            collect(DISTINCT s.name) AS symptoms,
            collect(DISTINCT dr.name) AS drugs,
            collect(DISTINCT t.name) AS treatments,
            collect(DISTINCT p.title) AS papers
        LIMIT $k
        """

    elif entity_type == "drug":
        cypher = """
                MATCH (dr:Drug)
        WHERE ANY(word IN $keywords WHERE toLower(dr.name) CONTAINS word)

        MATCH (dr)-[:TREATS]->(d:Disease)
        OPTIONAL MATCH (d)-[:ASSOCIATED_WITH]->(s:Symptom)
        OPTIONAL MATCH (t:Treatment)-[:TREATS]->(d)
        OPTIONAL MATCH (p:Paper)-[:MENTIONS]->(d)

        RETURN 
            d.name AS disease,
            collect(DISTINCT s.name) AS symptoms,
            collect(DISTINCT dr.name) AS drugs,
            collect(DISTINCT t.name) AS treatments,
            collect(DISTINCT p.title) AS papers
        LIMIT $k
        """

    elif entity_type == "treatment":
        cypher = """
                MATCH (t:Treatment)
        WHERE ANY(word IN $keywords WHERE toLower(t.name) CONTAINS word)

        MATCH (t)-[:TREATS]->(d:Disease)
        OPTIONAL MATCH (d)-[:ASSOCIATED_WITH]->(s:Symptom)
        OPTIONAL MATCH (d)<-[:TREATS]-(dr:Drug)
        OPTIONAL MATCH (p:Paper)-[:MENTIONS]->(d)

        RETURN 
            d.name AS disease,
            collect(DISTINCT s.name) AS symptoms,
            collect(DISTINCT dr.name) AS drugs,
            collect(DISTINCT t.name) AS treatments,
            collect(DISTINCT p.title) AS papers
        LIMIT $k
        """

    elif entity_type == "paper":
        cypher = """
                MATCH (p:Paper)
        WHERE ANY(word IN $keywords WHERE toLower(p.title) CONTAINS word)

        OPTIONAL MATCH (p)-[:MENTIONS]->(d:Disease)
        OPTIONAL MATCH (d)-[:ASSOCIATED_WITH]->(s:Symptom)
        OPTIONAL MATCH (d)<-[:TREATS]-(dr:Drug)
        OPTIONAL MATCH (t:Treatment)-[:TREATS]->(d)

        RETURN 
            d.name AS disease,
            collect(DISTINCT s.name) AS symptoms,
            collect(DISTINCT dr.name) AS drugs,
            collect(DISTINCT t.name) AS treatments,
            collect(DISTINCT p.title) AS papers
        LIMIT $k
        """

    else:
        print("[DEBUG] Unknown entity type")
        return []

    # -------------------------------
    # STEP 3: Run query
    # -------------------------------
    results = client.run_query(
        cypher,
        {"keywords": keywords, "k": k}
    )

    print(f"[DEBUG] Raw Results: {results}")

    # -------------------------------
    # STEP 4: Format output
    # -------------------------------
    docs = [r.get("result", "") for r in results]

    return docs




    