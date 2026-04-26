from core.gemini_client import generate_response
import json

def extract_entities(query):
    prompt = f"""
Extract important medical entities from the query.

Focus on:
- diseases
- symptoms
- treatments
- drugs
- biomarkers
- risk factors

Return JSON ONLY:
{{
  "entities": [
    {{"entity": "...", "type": "disease"}},
    {{"entity": "...", "type": "treatment"}}
  ]
}}

Query: {query}
"""

    ans = generate_response(prompt).strip()
    print("\n[LLM RAW ENTITIES]:", ans)

    ans = ans.replace("```json", "").replace("```", "").strip()

    try:
        data = json.loads(ans)
        entities = data.get("entities", [])

        cleaned = []
        for e in entities:
            if "entity" in e and "type" in e:
                cleaned.append({
                    "entity": e["entity"].lower(),
                    "type": e["type"].lower()
                })

        return cleaned[:5]

    except:
        return [{"entity": query.lower(), "type": "disease"}]