from graph.neo4j_client import Neo4jClient

client = Neo4jClient()


def traverse_graph(matched_nodes, paths, k=5):

    if not matched_nodes:
        print("[DEBUG] No nodes for traversal")
        return []
    if not paths:
        print("[DEBUG] No paths selected → skipping graph traversal")
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
        cypher ="""
    MATCH (n)
    WHERE ANY(word IN $keywords WHERE 
        toLower(coalesce(n.name, n.title)) CONTAINS word)

    OPTIONAL MATCH (n)-[r1]->(d:Disease)
    WHERE type(r1) IN $paths

    OPTIONAL MATCH (d)-[r2]->(s:Symptom)
    WHERE type(r2) IN $paths

    OPTIONAL MATCH (dr:Drug)-[r3]->(d)
    WHERE type(r3) IN $paths

    OPTIONAL MATCH (t:Treatment)-[r4]->(d)
    WHERE type(r4) IN $paths

    OPTIONAL MATCH (p:Paper)-[r5]->(d)
    WHERE type(r5) IN $paths

    RETURN 
        d.name AS disease,
        collect(DISTINCT s.name) AS symptoms,
        collect(DISTINCT dr.name) AS drugs,
        collect(DISTINCT t.name) AS treatments,
        collect(DISTINCT p.title) AS papers,
        collect(DISTINCT type(r1)) AS used_relations
    LIMIT $k
    """

        query_results = client.run_query(
            cypher,
            {"keywords": keywords, "k": k,"paths":paths}
        )

        print(f"\n[DEBUG] Traversal Results for '{value}':", query_results)

        results.extend(query_results)

    return results