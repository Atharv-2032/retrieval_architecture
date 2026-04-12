from core.gemini_client import generate_response
from core.utils import extract_json


def select_traversal_paths(query, matched_nodes):
    if not matched_nodes:
        print("[DEBUG] No matched nodes provided to path selector")
        return []

    # -------------------------------
    # Format nodes for LLM
    # -------------------------------
    node_text = "\n".join([
        f"{n['values']} ({', '.join(n['label'])})"
        for n in matched_nodes
    ])

    # -------------------------------
    # Prompt
    # -------------------------------
    prompt = f"""
You are assisting in querying a medical knowledge graph.

User Query:
{query}

Available entities and their types:
{node_text}

The graph contains these relationships:
- ASSOCIATED_WITH (connects diseases and symptoms)
- TREATS (connects drugs/treatments to diseases)
- MENTIONS (connects papers to diseases)

Your task:
Select the MOST relevant relationships to explore to answer the query.

Rules:
- Only choose relationships relevant to the query
- Choose at most 2–3 relationships
- Prefer precise relationships over broad ones
- Do NOT include irrelevant relationships

Return JSON ONLY:
{{
  "paths": ["ASSOCIATED_WITH"]
}}
"""

    # -------------------------------
    # Call LLM
    # -------------------------------
    ans = generate_response(prompt)
    print("\n[LLM PATH SELECTION RAW]:", ans)

    # -------------------------------
    # Robust JSON extraction
    # -------------------------------
    data = extract_json(ans)
    paths = data.get("paths", [])

    # -------------------------------
    # Validate paths
    # -------------------------------
    valid_paths = {"ASSOCIATED_WITH", "TREATS", "MENTIONS"}
    paths = [p for p in paths if p in valid_paths]

    print("[DEBUG] Selected Paths:", paths)

    return paths