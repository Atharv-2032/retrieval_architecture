from langgraph.graph import StateGraph

from core.graph_state import GraphState
from core.common_nodes import prompt_node, llm_node
from vector.vector_nodes import retrieve_node


builder = StateGraph(GraphState)

builder.add_node("retrieve", retrieve_node)
builder.add_node("prompt", prompt_node)
builder.add_node("llm", llm_node)

builder.set_entry_point("retrieve")
builder.add_edge("retrieve", "prompt")
builder.add_edge("prompt", "llm")
builder.set_finish_point("llm")

graph = builder.compile()





def run():
    print("Vector RAG Assistant (type 'exit' to stop)\n")

   

 
    query = input("You: ")

    state = {
            "query": query,
            "retrieved_docs": [],
            "prompt": "",
            "ans": "",
            
        }

    result = graph.invoke(state)

    answer = result["ans"]
        

    print("\nAssistant:\n")
    print(answer)

       


if __name__ == "__main__":
    run()
def run_vector_query(query):
    state = {
        "query": query,
        "retrieved_docs": [],
        "prompt": "",
        "ans": ""
    }

    result = graph.invoke(state)

    return {
        "answer": result["ans"],
        "retrieved_docs": result["retrieved_docs"]
    }