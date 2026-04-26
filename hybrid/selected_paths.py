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

TASK:
Return ONLY the relevant relationship TYPES.

STRICT RULES:
- Output must be a list of STRINGS
- Each item must be ONE of the relationships above
- DO NOT return entities
- DO NOT return triples
- DO NOT return nested lists
- DO NOT explain anything

If you violate this format, the system will FAIL.

Correct example:
{{
  "paths": ["TREATS", "HAS_SYMPTOM"]
}}

Wrong example (DO NOT DO THIS):
{{
  "paths": [["disease", "TREATS", "drug"]]
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

    paths = data.get("paths", [])

    # 🚨 STRICT VALIDATION (no silent fixing)
    if not isinstance(paths, list):
        raise ValueError(f"Invalid format: paths is not a list → {paths}")

    for p in paths:
        if not isinstance(p, str):
            raise ValueError(f"Invalid path (not string): {p}")

        if p not in valid_paths:
            raise ValueError(f"Invalid path (not allowed): {p}")

    print("[DEBUG] Selected Paths:", paths)

    return paths