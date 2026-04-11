from core.prompt_builder import build_prompt
from core.gemini_client import generate_response


def prompt_node(state):
    state["prompt"] = build_prompt(
        state["query"],
        state["retrieved_docs"],
        
    )
    return state


def llm_node(state):
    state["ans"] = generate_response(state["prompt"])
    return state