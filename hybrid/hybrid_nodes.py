from vector.retrieve import retrieve as vector_retrieve
from graph.retrieve_graph import retrieve as graph_retrieve

def  hybrid_retrieve_node(state):
    query = state["query"]

    vector_docs = vector_retrieve(query)
    graph_docs = graph_retrieve(query)

    combined_docs = []

    if vector_docs:
        combined_docs.extend(vector_docs)
    if graph_docs:
        combined_docs.extend(graph_docs)
    
    combined_docs = combined_docs[:5]

    state["retrieved_docs"] = combined_docs

    return state