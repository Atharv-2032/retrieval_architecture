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


user_profile = {
    "allergies": ["aspirin"],
    "conditions": [],
    "history": ["gastro-intestinal problems"],
    "family_history": ["diabetes", "high blood pressure", "heart issues"],
    "age": 45
}


def run():
    print("Vector RAG Assistant (type 'exit' to stop)\n")

    chat_history = []

    while True:
        query = input("You: ")

        if query.lower() == "exit":
            print("Session Ended")
            break

        chat_history.append(f"User: {query}")

        state = {
            "query": query,
            "retrieved_docs": [],
            "prompt": "",
            "ans": "",
            "chat_history": chat_history[-6:],
            "user_profile": user_profile
        }

        result = graph.invoke(state)

        answer = result["ans"]

        print("\nAssistant:\n")
        print(answer)

        chat_history.append(f"Assistant: {answer}")


if __name__ == "__main__":
    run()