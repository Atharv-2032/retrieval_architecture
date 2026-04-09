from vector.retrieve import retrieve

def retrieve_node(state):
    docs = retrieve(state["query"])
    state["retrieved_docs"] = docs
    return state