from graph.neo4j_client import Neo4jClient

client = Neo4jClient()


def traverse_graph(matched_nodes, paths, k=5):

    if not matched_nodes:
        print("[DEBUG] No nodes for traversal")
        return []

    results = []

    # -------------------------------
    # Loop through matched nodes
    # -------------------------------
    for node in matched_nodes:
        value = node["values"]

        keywords = value.lower().split()

        # -------------------------------
        # FINAL QUERY (ALL MATCHES ALWAYS INCLUDED)
        # -------------------------------
        cypher = """
        MATCH (n)
        WHERE ANY(word IN $keywords WHERE 
            toLower(coalesce(n.name, n.title)) CONTAINS word)

        OPTIONAL MATCH (n)-[:ASSOCIATED_WITH]->(d:Disease)
        OPTIONAL MATCH (d)-[:ASSOCIATED_WITH]->(s:Symptom)

        OPTIONAL MATCH (t:Treatment)-[:TREATS]->(d)
        OPTIONAL MATCH (dr:Drug)-[:TREATS]->(d)

        OPTIONAL MATCH (p:Paper)-[:MENTIONS]->(d)

        RETURN 
            d.name AS disease,
            collect(DISTINCT s.name) AS symptoms,
            collect(DISTINCT dr.name) AS drugs,
            collect(DISTINCT t.name) AS treatments,
            collect(DISTINCT p.title) AS papers
        LIMIT $k
        """

        query_results = client.run_query(
            cypher,
            {"keywords": keywords, "k": k}
        )

        print(f"\n[DEBUG] Traversal Results for '{value}':", query_results)

        results.extend(query_results)

    return results