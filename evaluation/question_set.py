import json
import time
import random
import os
from graph.neo4j_client import Neo4jClient
from core.gemini_client import generate_response

client = Neo4jClient()


# ── Graph data fetchers ─────────────────────────────────────────────
def fetch_single_hop():
    return client.run_query("""
        MATCH (a)-[r]->(b)
        WHERE r.context IS NOT NULL
          AND (a.name IS NOT NULL OR a.title IS NOT NULL)
          AND (b.name IS NOT NULL OR b.title IS NOT NULL)
        WITH coalesce(a.name, a.title) AS a_name,
             coalesce(b.name, b.title) AS b_name,
             labels(a) AS a_labels,
             labels(b) AS b_labels,
             type(r)   AS rel_type,
             r.context AS context
        RETURN a_name, b_name, a_labels, b_labels, rel_type, context
        ORDER BY rand()
        LIMIT 300
    """)


def fetch_multi_hop():
    return client.run_query("""
        MATCH (a)-[r1]->(b)-[r2]->(c)
        WHERE r1.context IS NOT NULL
          AND r2.context IS NOT NULL
          AND (a.name IS NOT NULL OR a.title IS NOT NULL)
          AND (b.name IS NOT NULL OR b.title IS NOT NULL)
          AND (c.name IS NOT NULL OR c.title IS NOT NULL)
        WITH coalesce(a.name, a.title) AS a_name,
             coalesce(b.name, b.title) AS b_name,
             coalesce(c.name, c.title) AS c_name,
             labels(a) AS a_labels,
             labels(b) AS b_labels,
             labels(c) AS c_labels,
             type(r1)   AS rel1,
             type(r2)   AS rel2,
             r1.context AS context1,
             r2.context AS context2
        RETURN a_name, b_name, c_name, a_labels, b_labels, c_labels,
               rel1, rel2, context1, context2
        ORDER BY rand()
        LIMIT 200
    """)


def fetch_aggregative():
    return client.run_query("""
        MATCH (a)-[r]->(b)
        WHERE r.context IS NOT NULL
          AND (a.name IS NOT NULL OR a.title IS NOT NULL)
        WITH coalesce(a.name, a.title) AS a_name,
             labels(a) AS a_labels,
             collect({
                 rel:     type(r),
                 target:  coalesce(b.name, b.title),
                 context: r.context
             }) AS connections
        WHERE size(connections) >= 3
        RETURN a_name, a_labels, connections
        ORDER BY rand()
        LIMIT 100
    """)


# ── Question generators ─────────────────────────────────────────────
def generate_single_hop_question(row):
    return f"""
You are building an evaluation dataset for a biomedical RAG system.

Given this medical knowledge graph fact:
- Entity A: {row['a_name']} (type: {row['a_labels']})
- Relationship: {row['rel_type']}
- Entity B: {row['b_name']} (type: {row['b_labels']})
- Context: {row['context']}

Generate one clear, specific medical question that:
- Can be answered using ONLY the context above
- Does not assume the relationship in the question
- Is specific and natural

Return JSON only:
{{
    "question": "...",
    "hop_type": "single",
    "entity_types": {json.dumps(row['a_labels'] + row['b_labels'])},
    "relationship": "{row['rel_type']}"
}}
"""


def generate_multi_hop_question(row):
    return f"""
You are building an evaluation dataset for a biomedical RAG system.

Given this two-hop chain:
- Entity A: {row['a_name']}
- Entity B: {row['b_name']}
- Entity C: {row['c_name']}
- Context 1: {row['context1']}
- Context 2: {row['context2']}

Generate one question that:
- Requires BOTH contexts to answer
- Is specific and natural

Return JSON only:
{{
    "question": "...",
    "hop_type": "multi",
    "entity_types": {json.dumps(row['a_labels'] + row['b_labels'] + row['c_labels'])},
    "relationships": ["{row['rel1']}", "{row['rel2']}"]
}}
"""


def generate_aggregative_question(row):
    connections_text = "\n".join([
        f"- {c['rel']} → {c['target']}: {c['context']}"
        for c in row['connections'][:5]
    ])

    return f"""
You are building an evaluation dataset for a biomedical RAG system.

Given:
- Entity: {row['a_name']}
- Connections:
{connections_text}

Generate one question that:
- Requires combining multiple connections
- Asks for a list, summary, or comparison

Return JSON only:
{{
    "question": "...",
    "hop_type": "aggregative",
    "entity_types": {json.dumps(row['a_labels'])},
    "relationships": {json.dumps(list(set([c['rel'] for c in row['connections'][:5]])))}
}}
"""


# ── LLM caller with retry ───────────────────────────────────────────
def call_llm_with_retry(prompt, retries=3):
    for attempt in range(retries):
        try:
            ans = generate_response(prompt).strip()
            ans = ans.replace("```json", "").replace("```", "").strip()
            data = json.loads(ans)
            if "question" in data:
                return data
        except Exception as e:
            print(f"  [WARN] Attempt {attempt+1} failed: {e}")
            time.sleep(2)
    return None


# ── Main generation pipeline ────────────────────────────────────────
def generate_question_set():

    questions = []

    targets = {
        "single":      30,
        "multi":       25,
        "aggregative": 20,
    }

    # --- single hop ---
    print("\n[1/3] Generating single-hop questions...")
    single_rows = fetch_single_hop()
    random.shuffle(single_rows)
    for row in single_rows:
        if len([q for q in questions if q["hop_type"] == "single"]) >= targets["single"]:
            break

        prompt = generate_single_hop_question(row)
        result = call_llm_with_retry(prompt)

        if result:
            result["context"] = row["context"]  # inject context
            questions.append(result)

            count = len([q for q in questions if q['hop_type'] == 'single'])
            print(f"  [single {count}/{targets['single']}]: {result['question'][:70]}...")

        time.sleep(1)

    # --- multi hop ---
    print("\n[2/3] Generating multi-hop questions...")
    multi_rows = fetch_multi_hop()
    random.shuffle(multi_rows)
    for row in multi_rows:
        if len([q for q in questions if q["hop_type"] == "multi"]) >= targets["multi"]:
            break

        prompt = generate_multi_hop_question(row)
        result = call_llm_with_retry(prompt)

        if result:
            result["context"] = row["context1"] + " " + row["context2"]
            questions.append(result)

            count = len([q for q in questions if q['hop_type'] == 'multi'])
            print(f"  [multi {count}/{targets['multi']}]: {result['question'][:70]}...")

        time.sleep(1)

    # --- aggregative ---
    print("\n[3/3] Generating aggregative questions...")
    agg_rows = fetch_aggregative()
    random.shuffle(agg_rows)
    for row in agg_rows:
        if len([q for q in questions if q["hop_type"] == "aggregative"]) >= targets["aggregative"]:
            break

        prompt = generate_aggregative_question(row)
        result = call_llm_with_retry(prompt)

        # rebuild connections_text for context injection
        connections_text = "\n".join([
            f"- {c['rel']} → {c['target']}: {c['context']}"
            for c in row['connections'][:5]
        ])

        if result:
            result["context"] = connections_text
            questions.append(result)

            count = len([q for q in questions if q['hop_type'] == 'aggregative'])
            print(f"  [aggregative {count}/{targets['aggregative']}]: {result['question'][:70]}...")

        time.sleep(1)

    return questions


# ── Save ────────────────────────────────────────────────────────────
def save_question_set(questions, path="evaluation/question_set.json"):
    dir_name = os.path.dirname(path)
    if dir_name:
        os.makedirs(dir_name, exist_ok=True)

    with open(path, "w") as f:
        json.dump(questions, f, indent=2)

    print(f"\n[DONE] Saved {len(questions)} questions to {path}")

    from collections import Counter
    types = Counter(q["hop_type"] for q in questions)

    print("\nDistribution:")
    for k, v in types.items():
        print(f"  {k}: {v}")


# ── Entry point ─────────────────────────────────────────────────────
if __name__ == "__main__":
    questions = generate_question_set()
    save_question_set(questions)
    client.close()