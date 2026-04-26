from core.gemini_client import generate_response
from core.utils import extract_json

def select_traversal_paths(query, entities):

    entity_text = "\n".join([
        f"{e['entity']} ({e['type']})"
        for e in entities
    ])

    prompt = f"""
Select the most relevant graph relationships based on the Query and Entities given below.

Query:
{query}

Entities:
{entity_text}

Available relationships:
- HAS_SYMPTOM
- TREATS
- RISK_FACTOR_FOR
- CAUSES
- PREVENTS
- INTERACTS_WITH
- AFFECTS
- ASSOCIATED_WITH
- IMPROVES
- MENTIONS

Return JSON:
{{
  "paths": ["TREATS", "IMPROVES"]
}}
"""

    ans = generate_response(prompt)
    print("\n[LLM PATH RAW]:", ans)

    data = extract_json(ans)

    valid = {
        "HAS_SYMPTOM", "TREATS", "RISK_FACTOR_FOR",
        "CAUSES", "PREVENTS", "INTERACTS_WITH",
        "AFFECTS", "ASSOCIATED_WITH", "MENTIONS", "IMPROVES"
    }

    paths = data.get("paths", [])
    paths = [p for p in paths if p in valid]

    return paths if paths else ["ASSOCIATED_WITH"]