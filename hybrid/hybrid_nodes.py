from vector.retrieve import retrieve as vector_retrieve
from vector.retrieve import retrieve as vector_retrieve
from hybrid.extract_entity_from_vector import extract_entities_from_docs
from hybrid.match_entities import match_entities
from hybrid.selected_paths import select_traversal_paths
from hybrid.traverse_graph import traverse_graph

def  hybrid_retrieve_node(state):
    query = state["query"]

    vector_docs = vector_retrieve(query)

    entities = extract_entities_from_docs(vector_docs)
    print("\n[STEP 2] Entities:", entities)


    matched_nodes = match_entities(entities)
    print("\n[STEP 3] Matched Nodes:", matched_nodes)

   
    paths = select_traversal_paths(query, matched_nodes)
    print("\n[STEP 4] Paths:", paths)

    
    graph_results = traverse_graph(matched_nodes, paths)
    print("\n[STEP 5] Graph Results:", graph_results)

    graph_docs = []

    for r in graph_results:
        text = ""

        if r.get("disease"):
            text += f"Disease: {r['disease']}\n"

        if r.get("symptoms"):
            text += "Symptoms: " + ", ".join(r["symptoms"][:5]) + "\n"

        if r.get("drugs"):
            text += "Drugs: " + ", ".join(r["drugs"][:5]) + "\n"

        if r.get("treatments"):
            text += "Treatments: " + ", ".join(r["treatments"][:5]) + "\n"

        if r.get("papers"):
            text += "Evidence: " + ", ".join(r["papers"][:3]) + "\n"

        if text.strip():
            graph_docs.append(text)
    combined_docs = []

    combined_docs.extend(vector_docs[:4])
    combined_docs.extend(graph_docs[:4])

    

    print("\n[FINAL CONTEXT]:", combined_docs)
    state["retrieved_docs"] = combined_docs
    return state