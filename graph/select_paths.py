from core.gemini_client import generate_response
from core.utils import extract_json

def select_traversal_paths(query, entities):

    entity_text = "\n".join([
        f"{e['entity']} ({e['type']})"
        for e in entities
    ])
    prompt = f"""
You are a biomedical knowledge graph expert. Your job is to select which relationship types to traverse in a Neo4j graph to best answer a medical query.

Query:
{query}

Extracted entities:
{entity_text}

Available relationships and what they mean:
- HAS_SYMPTOM     : disease → symptom (use when query asks about symptoms, presentation, signs)
- TREATS          : drug/treatment → disease (use when query asks about treatment options, therapy)
- RISK_FACTOR_FOR : risk_factor → disease (use when query asks about risk, predisposition, likelihood)
- CAUSES          : disease/factor → disease/symptom (use when query asks about etiology, cause, mechanism)
- PREVENTS        : drug/treatment → disease (use when query asks about prevention, prophylaxis)
- INTERACTS_WITH  : drug → drug (use when query involves multiple drugs or drug safety)
- AFFECTS         : factor → disease/organ (use when query asks about impact or effect)
- ASSOCIATED_WITH : any → any (broad association, use as fallback or when connection is unclear)
- MENTIONS        : paper → any entity (use when query asks for research evidence or citations)

Selection rules:
1. Pick only relationships that are DIRECTLY useful for answering this specific query
2. Prefer specific relationships over ASSOCIATED_WITH when possible
3. Include MENTIONS if the query asks for evidence, studies, or research
4. Return 2-4 relationships maximum — more is not better
5. Think about the entity TYPES present: 
   - disease + symptom entities → HAS_SYMPTOM, CAUSES
   - drug/treatment entities → TREATS, PREVENTS, INTERACTS_WITH
   - risk factor entities → RISK_FACTOR_FOR, AFFECTS

Return JSON only, no explanation:
{{
  "paths": ["TREATS", "PREVENTS"],
  "reasoning": "brief one-line reason"
}}
"""
    ans = generate_response(prompt)
    print("\n[LLM PATH RAW]:", ans)

    data = extract_json(ans)

    valid = {
        "HAS_SYMPTOM", "TREATS", "RISK_FACTOR_FOR",
        "CAUSES", "PREVENTS", "INTERACTS_WITH",
        "AFFECTS", "ASSOCIATED_WITH", "MENTIONS"
    }
    print("[DEBUG] Path reasoning:", data.get("reasoning", "")) 
    paths = data.get("paths", [])
    paths = [p for p in paths if p in valid]

    return paths if paths else ["ASSOCIATED_WITH"]