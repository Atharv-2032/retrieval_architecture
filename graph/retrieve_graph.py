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

    # -------------------------------
    # Scoring block (shared)
    # -------------------------------
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
    # STEP 2: Query selection
    # -------------------------------

    if entity_type == "disease":
        cypher = f"""
        MATCH (d:Disease)
        {scoring_block("d")}

        // Tier 1
        OPTIONAL MATCH (d)-[:HAS_SYMPTOM]->(s:Symptom)
        OPTIONAL MATCH (rf:RiskFactor)-[:RISK_FACTOR_FOR]->(d)
        OPTIONAL MATCH (dr:Drug)-[:TREATS]->(d)
        OPTIONAL MATCH (t:Treatment)-[:TREATS]->(d)

        // Tier 2
        OPTIONAL MATCH (d)-[:CAUSES]->(d2:Disease)
        OPTIONAL MATCH (t)-[:PREVENTS]->(d)
        OPTIONAL MATCH (d)-[:AFFECTS]->(x)

        // Collect strong signals
        WITH d,
             collect(DISTINCT s.name) AS symptoms,
             collect(DISTINCT rf.name) AS risk_factors,
             collect(DISTINCT dr.name) AS drugs,
             collect(DISTINCT t.name) AS treatments,
             collect(DISTINCT d2.name) AS caused_diseases,
             collect(DISTINCT x.name) AS affected_entities

        // 🔥 CONDITIONAL FALLBACK FLAG
        WITH d, symptoms, risk_factors, drugs, treatments, caused_diseases, affected_entities,
             (size(symptoms) = 0 AND size(risk_factors) = 0 AND size(drugs) = 0 AND size(treatments) = 0) AS need_fallback

        // Tier 3 (only if needed)
        OPTIONAL MATCH (d)-[:ASSOCIATED_WITH]->(aw)
        WHERE need_fallback

        OPTIONAL MATCH (p:Paper)-[:MENTIONS]->(d)

        RETURN 
            d.name AS disease,
            symptoms,
            risk_factors,
            drugs,
            treatments,
            caused_diseases,
            affected_entities,
            collect(DISTINCT aw.name) AS associated_entities,
            collect(DISTINCT p.title) AS papers
        """

    elif entity_type == "symptom":
        cypher = f"""
        MATCH (s:Symptom)
        {scoring_block("s")}

        MATCH (d:Disease)-[:HAS_SYMPTOM]->(s)

        OPTIONAL MATCH (rf:RiskFactor)-[:RISK_FACTOR_FOR]->(d)
        OPTIONAL MATCH (d)-[:CAUSES]->(d2:Disease)
        OPTIONAL MATCH (dr:Drug)-[:TREATS]->(d)
        OPTIONAL MATCH (d)-[:AFFECTS]->(x)

        OPTIONAL MATCH (p:Paper)-[:MENTIONS]->(d)

        RETURN 
            d.name AS disease,
            collect(DISTINCT s.name) AS symptoms,
            collect(DISTINCT rf.name) AS risk_factors,
            collect(DISTINCT dr.name) AS drugs,
            collect(DISTINCT d2.name) AS caused_diseases,
            collect(DISTINCT x.name) AS affected_entities,
            collect(DISTINCT p.title) AS papers
        """

    elif entity_type == "drug":
        cypher = f"""
        MATCH (dr:Drug)
        {scoring_block("dr")}

        MATCH (dr)-[:TREATS]->(d:Disease)

        OPTIONAL MATCH (dr)-[:INTERACTS_WITH]->(dr2:Drug)
        OPTIONAL MATCH (d)-[:HAS_SYMPTOM]->(s:Symptom)
        OPTIONAL MATCH (rf:RiskFactor)-[:RISK_FACTOR_FOR]->(d)
        OPTIONAL MATCH (d)-[:AFFECTS]->(x)

        OPTIONAL MATCH (p:Paper)-[:MENTIONS]->(d)

        RETURN 
            d.name AS disease,
            collect(DISTINCT s.name) AS symptoms,
            collect(DISTINCT rf.name) AS risk_factors,
            collect(DISTINCT dr2.name) AS interactions,
            collect(DISTINCT x.name) AS affected_entities,
            collect(DISTINCT p.title) AS papers
        """

    elif entity_type == "treatment":
        cypher = f"""
        MATCH (t:Treatment)
        {scoring_block("t")}

        MATCH (t)-[:TREATS]->(d:Disease)

        OPTIONAL MATCH (t)-[:PREVENTS]->(d)
        OPTIONAL MATCH (d)-[:HAS_SYMPTOM]->(s:Symptom)
        OPTIONAL MATCH (rf:RiskFactor)-[:RISK_FACTOR_FOR]->(d)
        OPTIONAL MATCH (dr:Drug)-[:TREATS]->(d)
        OPTIONAL MATCH (d)-[:AFFECTS]->(x)

        OPTIONAL MATCH (p:Paper)-[:MENTIONS]->(d)

        RETURN 
            d.name AS disease,
            collect(DISTINCT s.name) AS symptoms,
            collect(DISTINCT rf.name) AS risk_factors,
            collect(DISTINCT dr.name) AS drugs,
            collect(DISTINCT t.name) AS treatments,
            collect(DISTINCT x.name) AS affected_entities,
            collect(DISTINCT p.title) AS papers
        """

    elif entity_type == "riskfactor":
        cypher = f"""
        MATCH (rf:RiskFactor)
        {scoring_block("rf")}

        MATCH (rf)-[:RISK_FACTOR_FOR]->(d:Disease)

        OPTIONAL MATCH (d)-[:HAS_SYMPTOM]->(s:Symptom)
        OPTIONAL MATCH (d)-[:CAUSES]->(d2:Disease)
        OPTIONAL MATCH (d)-[:AFFECTS]->(x)

        OPTIONAL MATCH (p:Paper)-[:MENTIONS]->(d)

        RETURN 
            d.name AS disease,
            collect(DISTINCT s.name) AS symptoms,
            collect(DISTINCT rf.name) AS risk_factors,
            collect(DISTINCT d2.name) AS caused_diseases,
            collect(DISTINCT x.name) AS affected_entities,
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
        OPTIONAL MATCH (d)-[:HAS_SYMPTOM]->(s:Symptom)
        OPTIONAL MATCH (rf:RiskFactor)-[:RISK_FACTOR_FOR]->(d)
        OPTIONAL MATCH (dr:Drug)-[:TREATS]->(d)
        OPTIONAL MATCH (t:Treatment)-[:TREATS]->(d)

        RETURN 
            d.name AS disease,
            collect(DISTINCT s.name) AS symptoms,
            collect(DISTINCT rf.name) AS risk_factors,
            collect(DISTINCT dr.name) AS drugs,
            collect(DISTINCT t.name) AS treatments,
            collect(DISTINCT p.title) AS papers
        """

    else:
        print("[DEBUG] Unknown entity type")
        return []

    # -------------------------------
    # STEP 3: Execute
    # -------------------------------
    results = client.run_query(
        cypher,
        {"entity": entity_clean, "k": k}
    )

    print(f"[DEBUG] Raw Results: {results}")

    # -------------------------------
    # STEP 4: Format Output
    # -------------------------------
    docs = []

    for r in results:
        text = ""

        if r.get("disease"):
            text += f"Disease: {r['disease']}\n"

        if r.get("symptoms"):
            text += "Symptoms: " + ", ".join(r["symptoms"][:5]) + "\n"

        if r.get("risk_factors"):
            text += "Risk Factors: " + ", ".join(r["risk_factors"][:5]) + "\n"

        if r.get("drugs"):
            text += "Drugs: " + ", ".join(r["drugs"][:5]) + "\n"

        if r.get("treatments"):
            text += "Treatments: " + ", ".join(r["treatments"][:5]) + "\n"

        if r.get("caused_diseases"):
            text += "Causes: " + ", ".join(r["caused_diseases"][:5]) + "\n"

        if r.get("affected_entities"):
            text += "Affects: " + ", ".join(r["affected_entities"][:5]) + "\n"

        if r.get("associated_entities"):
            text += "Associated: " + ", ".join(r["associated_entities"][:5]) + "\n"

        if r.get("papers"):
            text += "Evidence: " + ", ".join(r["papers"][:3]) + "\n"

        docs.append(text.strip())

    return docs