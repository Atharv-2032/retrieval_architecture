import json

from vector.run_vector import run_vector_query
from graph.run_graph import run_graph_query
from hybrid.run_hybrid import run_hybrid_query



data_input = [
    {
        "query": "Explain the role of Negative Pressure Wound Therapy in diabetic foot ulcer",
        "ground_truth": "Negative Pressure Wound Therapy improves healing in diabetic foot ulcers by promoting granulation tissue formation and increasing healing rates compared to standard care."
    },
    {
        "query": "How does topical capsaicin 0.075 compare to lower concentrations?",
        "ground_truth": "Topical capsaicin 0.075 percent is more effective than lower concentrations like 0.025 percent in reducing neuropathic pain, with manageable localized side effects."
    },
    {
        "query": "What were the outcomes of low vs high dose atorvastatin in macular edema?",
        "ground_truth": "Low-dose atorvastatin showed better improvements in visual acuity and macular thickness compared to high-dose when used with anti-VEGF therapy."
    }
]



dataset = []

for item in data_input:
    query = item["query"]
    ground_truth = item["ground_truth"]

    print(f"\nProcessing: {query}")

    vector_res = run_vector_query(query)
    graph_res = run_graph_query(query)
    hybrid_res = run_hybrid_query(query)

    # sanity check (important)
    for name, res in [("vector", vector_res), ("graph", graph_res), ("hybrid", hybrid_res)]:
        if "answer" not in res or "retrieved_docs" not in res:
            raise ValueError(f"{name} output format incorrect for query: {query}")

    dataset.append({
        "query": query,
        "vector": vector_res,
        "graph": graph_res,
        "hybrid": hybrid_res,
        "ground_truth": ground_truth
    })



with open("ragas_input.json", "w") as f:
    json.dump(dataset, f, indent=2)

print("\n ragas_input.json created")