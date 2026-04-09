from typing import List, Dict, TypedDict

class GraphState(TypedDict):
    query: str
    retrieved_docs: List[str]
    prompt: str
    ans: str
    chat_history: List[str]
    user_profile: Dict