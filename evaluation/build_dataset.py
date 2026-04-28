import json
import os
import sys
import time

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from vector.run_vector import run_vector_query
from graph.run_graph import run_graph_query
from hybrid.run_hybrid import run_hybrid_query

# ---------------------------
# CONFIG
# ---------------------------
GROUND_TRUTH_PATH = os.path.join(os.path.dirname(__file__), "ground_truths.json")
OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "ragas_input.json")

MAX_RETRIES = 3
RETRY_DELAYS = [5, 15, 30]  # seconds between retries — escalating backoff

# ---------------------------
# RETRY WRAPPER
# ---------------------------
def run_with_retry(fn, query, pipeline_name):
    """
    Wraps any pipeline query function with retry logic.
    Catches 503, rate limit, and general transient errors.
    Returns None if all retries exhausted.
    """
    for attempt in range(MAX_RETRIES):
        try:
            result = fn(query)

            # validate output format immediately
            if "answer" not in result or "retrieved_docs" not in result:
                raise ValueError(f"Invalid output format from {pipeline_name}")

            return result

        except Exception as e:
            error_str = str(e).lower()

            # identify retryable errors
            is_retryable = any(code in error_str for code in [
                "503", "502", "500",        # server errors
                "429", "rate limit",         # rate limiting
                "timeout", "timed out",      # timeouts
                "connection",                # connection errors
                "service unavailable",       # explicit 503 message
                "overloaded",               # model overloaded
                "resource exhausted"         # quota errors
            ])

            if attempt < MAX_RETRIES - 1 and is_retryable:
                delay = RETRY_DELAYS[attempt]
                print(f"  [{pipeline_name}] Attempt {attempt+1} failed: {e}")
                print(f"  [{pipeline_name}] Retrying in {delay}s...")
                time.sleep(delay)
            else:
                # either non-retryable error or final attempt
                print(f"  [{pipeline_name}] Failed after {attempt+1} attempts: {e}")
                return None

    return None


# ---------------------------
# LOAD GROUND TRUTHS
# ---------------------------
with open(GROUND_TRUTH_PATH, "r") as f:
    ground_truth_data = json.load(f)

data_input = [
    {
        "query":        item["question"],
        "ground_truth": item["ground_truth"]
    }
    for item in ground_truth_data
    if item["ground_truth"] not in ("INSUFFICIENT_CONTEXT", "GENERATION_FAILED")
]

print(f"Loaded {len(data_input)} questions with valid ground truths")

# ---------------------------
# RUN PIPELINES
# ---------------------------
dataset = []
skipped = []

for item in data_input:
    query        = item["query"]
    ground_truth = item["ground_truth"]

    print(f"\nProcessing: {query[:70]}...")

    vector_res = run_with_retry(run_vector_query, query, "vector")
    graph_res  = run_with_retry(run_graph_query,  query, "graph")
    hybrid_res = run_with_retry(run_hybrid_query, query, "hybrid")

    # if any pipeline completely failed after all retries — skip this question
    failed_pipelines = [
        name for name, res in [
            ("vector", vector_res),
            ("graph",  graph_res),
            ("hybrid", hybrid_res)
        ] if res is None
    ]

    if failed_pipelines:
        print(f"  [SKIP] {query[:60]}... — failed pipelines: {failed_pipelines}")
        skipped.append({
            "query":            query,
            "failed_pipelines": failed_pipelines
        })
        continue

    dataset.append({
        "query":        query,
        "vector":       vector_res,
        "graph":        graph_res,
        "hybrid":       hybrid_res,
        "ground_truth": ground_truth
    })

    print(f"  [OK] all 3 pipelines succeeded")

# ---------------------------
# SAVE
# ---------------------------
with open(OUTPUT_PATH, "w") as f:
    json.dump(dataset, f, indent=2)

print(f"\nDone.")
print(f"  Processed:  {len(dataset)}")
print(f"  Skipped:    {len(skipped)}")
print(f"  Saved to:   {OUTPUT_PATH}")

if skipped:
    skipped_path = os.path.join(os.path.dirname(__file__), "skipped_queries.json")
    with open(skipped_path, "w") as f:
        json.dump(skipped, f, indent=2)
    print(f"  Skipped queries saved to: {skipped_path}")
    print(f"  Re-run those manually or investigate the failing pipeline")