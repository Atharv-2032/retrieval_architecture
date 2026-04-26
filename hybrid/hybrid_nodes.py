from vector.retrieve import retrieve as vector_retrieve
from hybrid.extract_entity_from_vector import extract_entities_from_docs
from hybrid.match_entities import match_entities
from hybrid.selected_paths import select_traversal_paths
from hybrid.traverse_graph import traverse_graph


def hybrid_retrieve_node(state):
    query = state["query"]

    # STEP 1: Vector retrieval
    vector_docs = vector_retrieve(query)

    # STEP 2: Extract entities
    entities = extract_entities_from_docs(vector_docs)
    print("\n[STEP 2] Entities:", entities)

    # STEP 3: Match graph nodes
    matched_nodes = match_entities(entities)
    print("\n[STEP 3] Matched Nodes:", matched_nodes)

    # STEP 4: Select paths
    paths = select_traversal_paths(query, matched_nodes)
    print("\n[STEP 4] Paths:", paths)

    # STEP 5: Traverse graph
    graph_results = traverse_graph(matched_nodes, paths)
    print("\n[STEP 5] Graph Results:", graph_results)

    # STEP 6: Format graph docs
    graph_docs = []
    for r in graph_results:
        if r.get("context"):
            graph_docs.append(r["context"].strip())
    
    # STEP 7: Combine
    combined_docs = []
    combined_docs.extend(vector_docs[:4])
    combined_docs.extend(graph_docs[:4])

    print("\n[FINAL CONTEXT]:", combined_docs)

    state["retrieved_docs"] = combined_docs
    return state