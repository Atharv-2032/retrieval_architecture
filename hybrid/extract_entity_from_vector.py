from core.gemini_client import generate_response 
import json
def extract_entities_from_docs(docs):
    all_entities = set()

    for doc in docs[:3]:   # 🔥 only top-k chunks (important)
        prompt = f"""
        Extract the most important medical entities from the context below.

        Focus on:
        - diseases
        - symptoms
        - treatments
        - drugs
        - risk factors
        

        Return JSON ONLY:
        {{
        "entities": ["entity1", "entity2", ...]
        }}

        Context:
        {doc}
        """

        ans = generate_response(prompt)

        ans = ans.strip()
        if ans.startswith("```"):
            ans = ans.split("```")[1]
            if ans.startswith("json"):
                ans = ans[4:]
            ans = ans.strip()

        try:
            data = json.loads(ans)
            entities = [e.lower() for e in data.get("entities", [])]
            all_entities.update(entities)
        except Exception as e:
            print("[DEBUG] ENTITY PARSE ERROR:", e)

    return list(all_entities)
