import json

from vector.run_vector import run_vector_query
from graph.run_graph import run_graph_query
from hybrid.run_hybrid import run_hybrid_query



data_input = [
    {
        "query": "How is nurse-led rehabilitation related to asthma?",
        "ground_truth": "Nurse-led rehabilitation is associated with improved management of asthma, helping patients better handle their symptoms and overall condition in primary care"
    },
    {
        "query": "how are type 2 diabetes, cardiac strain markers (GLS and LAS), and Alzheimer's disease connected to cognitive impairment, and which markers or mechanisms are highlighted as early indicators or research focuses?",
        "ground_truth": "Cognitive impairment is centrally linked to type 2 diabetes and Alzheimer's disease, reflecting shared pathological mechanisms and research focus. The graph shows that cardiac dysfunction (heart failure, left ventricular and left atrial abnormalities) is associated with cognitive impairment, with GLS and especially LAS identified as early markers. Additionally, emerging research connects cognitive impairment in diabetes to molecular mechanisms, neuroinflammation, and interdisciplinary factors, highlighting a shift toward early detection and integrated biomarkers."
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