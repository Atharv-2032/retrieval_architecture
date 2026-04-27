
import json
import re
import random
import chromadb

from core.gemini_client import generate_response
from graph.neo4j_client import Neo4jClient


# =========================================
# 1. CONTEXT FILTER (CRITICAL FIX)
# =========================================
def is_valid_context(ctx):
    if not ctx:
        return False

    ctx = ctx.strip()

    if len(ctx) < 120:
        return False

    if ctx in ["o", "-", "C"]:
        return False

    if "." not in ctx:
        return False

    return True


# =========================================
# 2. GET VECTOR CONTEXTS
# =========================================
def get_vector_contexts(collection_name, n=100):
    client = chromadb.PersistentClient(path="./vector_db/chroma_storage")
    collection = client.get_collection(collection_name)

    data = collection.get(include=["documents"])
    docs = [d for sublist in data["documents"] for d in sublist]

    docs = [d for d in docs if is_valid_context(d)]

    random.shuffle(docs)

    print(f"[INFO] Clean vector docs: {len(docs)}")
    return docs[:n]


# =========================================
# 3. GET GRAPH CONTEXTS
# =========================================
def get_graph_contexts(n=100):
    client = Neo4jClient()

    cypher = """
    MATCH ()-[r]->()
    WHERE r.context IS NOT NULL
    RETURN r.context AS context
    """

    results = client.run_query(cypher)
    contexts = [r["context"] for r in results if r.get("context")]

    contexts = [c for c in contexts if is_valid_context(c)]

    random.shuffle(contexts)

    print(f"[INFO] Clean graph contexts: {len(contexts)}")
    return contexts[:n]


# =========================================
# 4. STRICT PROMPT
# =========================================
def build_prompt(context):
    return f"""
You are given a medical research excerpt.

Generate EXACTLY 4 questions that can be directly answered using ONLY this content.

STRICT RULES:
- Use specific medical entities (disease, treatment, outcome)
- DO NOT say: "this research", "this study", "the context"
- DO NOT ask vague or generic questions
- DO NOT invent information
- Each question MUST be answerable from the text

Types:
1. SINGLE: one fact
2. MULTI: combine 2 facts
3. COMPARISON: compare 2 items
4. NEGATIVE: unclear or missing info

Return JSON:
{{
  "questions": [
    {{"type": "single", "question": "..."}},
    {{"type": "multi", "question": "..."}},
    {{"type": "comparison", "question": "..."}},
    {{"type": "negative", "question": "..."}}
  ]
}}

Context:
{context}
"""


# =========================================
# 5. PARSE
# =========================================
def parse_questions(ans):
    ans = ans.strip().replace("```json", "").replace("```", "")

    match = re.search(r"\{.*\}", ans, re.DOTALL)
    if not match:
        return []

    try:
        return json.loads(match.group()).get("questions", [])
    except:
        return []


# =========================================
# 6. VALIDATE QUESTIONS
# =========================================
def validate_question(q):
    if "question" not in q or "type" not in q:
        return False

    text = q["question"].strip()

    if len(text) < 10 or not text.endswith("?"):
        return False

    if q["type"] not in ["single", "multi", "comparison", "negative"]:
        return False

    return True


# =========================================
# 7. FILTER BAD QUESTIONS
# =========================================
def is_bad_question(q):
    q = q.lower()

    bad_patterns = [
        "this research", "this study", "the context",
        "main purpose", "primary purpose",
        "what is described"
    ]

    return any(p in q for p in bad_patterns)


# =========================================
# 8. SAMPLE CONTEXTS (BALANCED)
# =========================================
def sample_contexts(vector_contexts, graph_contexts, k=10):
    contexts = vector_contexts[:k] + graph_contexts[:k]
    random.shuffle(contexts)

    print(f"[INFO] Using {k} vector + {k} graph contexts")
    return contexts


# =========================================
# 9. GENERATE QUESTIONS
# =========================================
def generate_questions(contexts):
    all_questions = []

    for i, ctx in enumerate(contexts):
        print(f"[INFO] Context {i+1}/{len(contexts)}")

        ctx = ctx[:1500]

        prompt = build_prompt(ctx)
        raw = generate_response(prompt)

        qs = parse_questions(raw)

        for q in qs:
            if validate_question(q) and not is_bad_question(q["question"]):
                all_questions.append({
                    "question": q["question"],
                    "type": q["type"],
                    "context": ctx
                })

    return all_questions


# =========================================
# 10. BALANCE QUESTIONS
# =========================================
def balance_questions(questions):
    buckets = {
        "single": [],
        "multi": [],
        "comparison": [],
        "negative": []
    }

    for q in questions:
        buckets[q["type"]].append(q)

    for k in buckets:
        random.shuffle(buckets[k])

    print("\n[DEBUG] Distribution:")
    for k in buckets:
        print(f"{k}: {len(buckets[k])}")

    return (
        buckets["single"][:15] +
        buckets["multi"][:15] +
        buckets["comparison"][:5] +
        buckets["negative"][:5]
    )


# =========================================
# 11. MAIN PIPELINE
# =========================================
def build_question_set(collection_name):
    print("\n[STEP 1] Fetching contexts")

    vector_contexts = get_vector_contexts(collection_name)
    graph_contexts = get_graph_contexts()

    print("\n[STEP 2] Sampling")
    contexts = sample_contexts(vector_contexts, graph_contexts, k=10)

    print("\n[STEP 3] Generating")
    questions = generate_questions(contexts)

    print("\n[STEP 4] Balancing")
    final = balance_questions(questions)

    print("\n=== SAMPLE OUTPUT ===")
    for q in final[:5]:
        print("\n---")
        print("TYPE:", q["type"])
        print("Q:", q["question"])
        print("CTX:", q["context"][:200])

    return final


# =========================================
# 12. SAVE
# =========================================
def save_questions(questions, path="questions_raw.json"):
    with open(path, "w") as f:
        json.dump(questions, f, indent=2)


# =========================================
# RUN
# =========================================
if __name__ == "__main__":
    COLLECTION_NAME = "langchain"

    questions = build_question_set(COLLECTION_NAME)
    save_questions(questions)