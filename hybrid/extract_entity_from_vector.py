from core.gemini_client import generate_response
import json

def extract_entities_from_docs(docs):
    text = "\n".join(docs)
    prompt =  f"""
    Extract the most important medical entities from the context below.

    Focus on:
    - diseases
    - symptoms
    - treatments
    - drugs

    Return JSON ONLY:
    {{
    "entities": ["entity1", "entity2", ...]
    }}

    Context:
    {text}
    """
    ans = generate_response(prompt)
    print(ans)

    ans = ans.strip()
    if ans.startswith("```"):
        ans = ans.split("```")[1]
        if ans.startswith("json"):
            ans = ans[4:]
        ans = ans.strip()
    
    try:
        data = json.loads(ans)
        entities = [e.lower() for e in data.get("entities", [])]
        return entities
    except Exception as e:
        print("[DEBUG] ENTITY PARSE ERROR:", e)
        return []
