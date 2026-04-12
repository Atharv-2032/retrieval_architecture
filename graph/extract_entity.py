from core.gemini_client import generate_response
import json
import re


def extract_entity(query):
    prompt = f"""
Extract the main medical entity from the query.

Return JSON ONLY:
{{
  "entity": "...",
  "type": "disease | symptom | drug | treatment | paper"
}}

Query: {query}
"""

    ans = generate_response(prompt).strip()
    print("\n[LLM RAW OUTPUT]:", ans)


    # 🔥 Remove markdown
    ans = ans.replace("```json", "").replace("```", "").strip()

    # 🔥 Extract JSON using regex (extra safe)
    match = re.search(r"\{.*\}", ans, re.DOTALL)
    try:
        data = json.loads(ans)
        return data["entity"].lower(), data["type"].lower()
    except:
        return query.lower(), "disease"
    