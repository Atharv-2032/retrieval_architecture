import json
import os
import sys
import time
from tqdm import tqdm
from rank_bm25 import BM25Okapi


sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from core.gemini_client import generate_response

# ---------------------------
# PATHS
# ---------------------------
PAPERS_PATH   = os.path.join(os.path.dirname(__file__), "..", "papers_data.json")
QUESTIONS_PATH = os.path.join(os.path.dirname(__file__), "question_set.json")
OUTPUT_PATH   = os.path.join(os.path.dirname(__file__), "ground_truths.json")
FLAGGED_PATH  = os.path.join(os.path.dirname(__file__), "flagged_for_review.json")

N_BY_HOP = {
    "single":      1,
    "multi":       3,
    "aggregative": 5
}

# ---------------------------
# LOAD
# ---------------------------
def load_papers(path):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    papers = []
    for p in data:
        text  = p.get("text", "").strip()
        title = p.get("metadata", {}).get("title", "")
        if text:
            papers.append({"text": text, "title": title})
    print(f"Loaded {len(papers)} papers")
    return papers


def load_questions(path):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    print(f"Loaded {len(data)} questions")
    return data


# ---------------------------
# BM25 INDEX
# ---------------------------
def build_bm25_index(papers):
    corpus = [(p["title"] + " " + p["text"]).lower().split() for p in papers]
    bm25   = BM25Okapi(corpus)
    print("BM25 index built")
    return bm25


# ---------------------------
# RETRIEVAL
# ---------------------------
def retrieve_abstracts(query, bm25, papers, n):
    scores     = bm25.get_scores(query.lower().split())
    top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:n]
    return [{"title": papers[i]["title"], "text": papers[i]["text"], "score": scores[i]}
            for i in top_indices]


def decompose_multi_hop(question):
    prompt = f"""You are helping build a biomedical evaluation dataset.

This multi-hop medical question bridges two concepts from two different sources:
{question}

Split into exactly 2 simple sub-questions, each answerable from a single paper.
Keep sub-questions short and keyword-rich.

Return JSON only:
{{"sub_questions": ["...", "..."]}}"""
    try:
        response = generate_response(prompt).strip()
        response = response.replace("```json", "").replace("```", "").strip()
        data     = json.loads(response)
        subs     = data.get("sub_questions", [])
        if len(subs) == 2:
            return subs
    except Exception as e:
        print(f"  [WARN] Decomposition failed: {e}")
    return [question, question]


def retrieve_by_hop_type(question, hop_type, bm25, papers):
    if hop_type == "single":
        return retrieve_abstracts(question, bm25, papers, n=1)

    elif hop_type == "multi":
        sub_questions = decompose_multi_hop(question)
        seen    = set()
        results = []
        for sub in sub_questions:
            candidates = retrieve_abstracts(sub, bm25, papers, n=2)
            for c in candidates:
                if c["title"] not in seen:
                    seen.add(c["title"])
                    results.append(c)
                    break
        # fallback if decomposition returned duplicates
        if len(results) < 2:
            for r in retrieve_abstracts(question, bm25, papers, n=3):
                if r["title"] not in seen:
                    seen.add(r["title"])
                    results.append(r)
        return results

    elif hop_type == "aggregative":
        return retrieve_abstracts(question, bm25, papers, n=5)

    else:
        return retrieve_abstracts(question, bm25, papers, n=3)


# ---------------------------
# CONTEXT STRING
# ---------------------------
def build_context_string(abstracts):
    if len(abstracts) == 1:
        return abstracts[0]["text"]
    parts = [f"[Source {i}: {a['title']}]\n{a['text']}"
             for i, a in enumerate(abstracts, 1)]
    return "\n\n".join(parts)


# ---------------------------
# GENERATE
# ---------------------------
def generate_ground_truth(question, context, hop_type, retries=3):
    if hop_type == "aggregative":
        instruction = ("You are answering a question that requires combining "
                       "information from multiple sources. Use ALL sources provided.")
    else:
        instruction = "Answer the question using ONLY the context provided below."

    prompt = f"""You are a precise medical information extractor.
{instruction}

Rules:
- Use ONLY information explicitly stated in the context
- Do NOT infer, extrapolate, or use outside knowledge
- Include specific numbers, statistics, drug names, and percentages exactly as written
- Keep answers concise (2-4 sentences max)
- If the context genuinely does not contain enough information,
  respond with exactly: INSUFFICIENT_CONTEXT
- Do NOT give partial answers mixed with INSUFFICIENT_CONTEXT

Context:
{context}

Question: {question}

Answer:"""

    for attempt in range(retries):
        try:
            answer = generate_response(prompt).strip()
            insufficient_phrases = [
                "insufficient", "not mentioned", "not provided",
                "cannot be answered", "no information", "does not mention",
                "not stated", "not specified", "not found", "not available"
            ]
            if any(p in answer.lower() for p in insufficient_phrases):
                return "INSUFFICIENT_CONTEXT"
            return answer
        except Exception as e:
            print(f"  [WARN] Attempt {attempt+1} failed: {e}")
            time.sleep(2 ** attempt)

    return "GENERATION_FAILED"


# ---------------------------
# MAIN
# ---------------------------
def main():
    papers    = load_papers("./papers_data.json")
    questions = load_questions("./evaluation/question_set.json")
    bm25      = build_bm25_index(papers)

    results             = []
    flagged             = []
    insufficient_count  = 0
    failed_count        = 0

    for item in tqdm(questions, desc="Generating ground truths"):
        question = item["question"]
        hop_type = item.get("hop_type", "single")

        abstracts = retrieve_by_hop_type(question, hop_type, bm25, papers)

        if not abstracts:
            print(f"  [SKIP] No abstracts for: {question[:70]}...")
            failed_count += 1
            continue

        context      = build_context_string(abstracts)
        ground_truth = generate_ground_truth(question, context, hop_type)

        entry = {
            "question":     question,
            "ground_truth": ground_truth,
            "hop_type":     hop_type,
            "source_abstracts": [
                {"title": a["title"], "bm25_score": round(a["score"], 3)}
                for a in abstracts
            ]
        }

        results.append(entry)

        if ground_truth == "INSUFFICIENT_CONTEXT":
            insufficient_count += 1
            flagged.append(entry)
            print(f"  [WARN] Insufficient: {question[:70]}...")
        elif ground_truth == "GENERATION_FAILED":
            failed_count += 1
            flagged.append(entry)
            print(f"  [FAIL] Failed: {question[:70]}...")

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    if flagged:
        with open(FLAGGED_PATH, "w", encoding="utf-8") as f:
            json.dump(flagged, f, indent=2, ensure_ascii=False)

    print(f"\nDone.")
    print(f"  Total:                {len(results)}")
    print(f"  Insufficient context: {insufficient_count}")
    print(f"  Failed:               {failed_count}")
    print(f"  Saved to:             {OUTPUT_PATH}")

    if flagged:
        print(f"\n  {len(flagged)} flagged for manual review → {FLAGGED_PATH}")
        print(f"  For each: check source_abstracts titles")
        print(f"  Wrong paper → write ground truth manually")
        print(f"  Right paper but no answer → remove question from set")


if __name__ == "__main__":
    main()