from graph.neo4j_client import Neo4jClient
from graph.extract_entity import extract_entity

client = Neo4jClient()


def retrieve(query, k=2):
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

    elif entity_type == "papers":
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
    docs = []

    for r in results:
        disease = r.get("disease", "")
        symptoms = r.get("symptoms", [])
        drugs = r.get("drugs", [])
        treatments = r.get("treatments", [])
        papers = r.get("papers", [])

        text = ""

        if disease:
            text += f"Disease: {disease}\n"

        if symptoms:
            text += "Symptoms: " + ", ".join(symptoms[:5]) + "\n"

        if drugs:
            text += "Drugs: " + ", ".join(drugs[:5]) + "\n"

        if treatments:
            text += "Treatments: " + ", ".join(treatments[:5]) + "\n"

        if papers:
            text += "Evidence: " + ", ".join(papers[:3]) + "\n"

        docs.append(text)

    return docs




    