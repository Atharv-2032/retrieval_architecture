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

    

    print(f"\n[DEBUG] Entity: {entity}, Type: {entity_type}")
    
    def scoring_block(var):
        return f"""
        WITH {var},
        toLower({var}.name) AS name,
        $entity AS entity

        WITH {var}, name, entity,
        CASE 
            WHEN name = entity THEN 5
            WHEN name STARTS WITH entity THEN 4
            WHEN entity STARTS WITH name THEN 4
            WHEN name CONTAINS entity THEN 3
            WHEN entity CONTAINS name THEN 3
            ELSE 0
        END AS score

        WHERE score > 0

        WITH {var}
        ORDER BY score DESC
        LIMIT $k
        """

    # -------------------------------
    # STEP 2: Choose simple query
    # -------------------------------

    if entity_type == "disease":
        cypher = f"""
        MATCH (d:Disease)
        {scoring_block("d")}

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
        """
        

    elif entity_type == "symptom":
        cypher = f"""
        MATCH (s:Symptom)
        {scoring_block("s")}

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
        """

    elif entity_type == "drug":
        cypher = f"""
        MATCH (dr:Drug)
        {scoring_block("dr")}

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
        """

    elif entity_type == "treatment":
        cypher = f"""
        MATCH (t:Treatment)
        {scoring_block("t")}

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
        """

    elif entity_type == "papers":
        cypher = f"""
        MATCH (p:Paper)
        WITH p,
        toLower(p.title) AS name,
        $entity AS entity

        WITH p, name, entity,
        CASE 
            WHEN name = entity THEN 5
            WHEN name STARTS WITH entity THEN 4
            WHEN entity STARTS WITH name THEN 4
            WHEN name CONTAINS entity THEN 3
            WHEN entity CONTAINS name THEN 3
            ELSE 0
        END AS score

        WHERE score > 0

        WITH p
        ORDER BY score DESC
        LIMIT $k

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
        """


    else:
        print("[DEBUG] Unknown entity type")
        return []

    # -------------------------------
    # STEP 3: Run query
    # -------------------------------
    results = client.run_query(
        cypher,
        {"entity": entity_clean, "k": k}
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




    