from graph.retrieve_graph import retrieve

def graph_retrieve_node(state):
    docs = retrieve(state["query"])
    state["retrieved_docs"] = docs
    return state
