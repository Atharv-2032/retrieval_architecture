from core.gemini_client import generate_response
from core.utils import extract_json

def select_traversal_paths(query, matched_nodes):
    if not matched_nodes:
        return []

    node_text = "\n".join([
        f"{n['values']} ({', '.join(n['label'])})"
        for n in matched_nodes
    ])

    prompt = f"""
You are assisting in querying a medical knowledge graph.

User Query:
{query}

Available entities:
{node_text}

Graph relationships:
- HAS_SYMPTOM
- TREATS
- RISK_FACTOR_FOR
- CAUSES
- PREVENTS
- INTERACTS_WITH
- AFFECTS
- ASSOCIATED_WITH
- MENTIONS

Rules:
- Prefer strong relations (HAS_SYMPTOM, TREATS, RISK_FACTOR_FOR)
- Use CAUSES / PREVENTS / AFFECTS when relevant
- Use ASSOCIATED_WITH only if needed
- Max 3 paths

Return JSON ONLY:
{{
  "paths": ["HAS_SYMPTOM"]
}}
"""

    ans = generate_response(prompt)
    print("\n[LLM PATH RAW]:", ans)

    data = extract_json(ans)

    valid_paths = {
        "HAS_SYMPTOM", "TREATS", "RISK_FACTOR_FOR",
        "CAUSES", "PREVENTS", "INTERACTS_WITH",
        "AFFECTS", "ASSOCIATED_WITH", "MENTIONS"
    }

    paths = [p for p in data.get("paths", []) if p in valid_paths]

    print("[DEBUG] Selected Paths:", paths)

    return paths