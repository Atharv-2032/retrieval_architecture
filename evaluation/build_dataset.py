import json

from vector.run_vector import run_vector_query
from graph.run_graph import run_graph_query
from hybrid.run_hybrid import run_hybrid_query



data_input = [
    {
        "query": "how does vitamin d affect diabetic peripheral neuropathy",
        "ground_truth": "Vitamin D supplementation may improve painful diabetic peripheral neuropathy (DPN) by reducing pain scores and improving quality of life. Its effects are linked to anti-inflammatory action, promotion of nerve regeneration, and increased neurotrophic factors. However, evidence is limited and requires further randomized trials to confirm efficacy and optimal treatment protocols."
    },
    {
        "query": "What is the metabolically obese normal weight (MONW) phenotype in children, and what are its prevalence, key metabolic features, and early-life risk factors?",
        "ground_truth": "The MONW phenotype refers to children with normal BMI but adverse metabolic abnormalities. Its prevalence ranges from 10.6% to 56.2%. Affected children show visceral adiposity, insulin resistance, dyslipidaemia, hypertension, impaired glucose metabolism, and low-grade inflammation. Key early-life risk factors include extreme birth weight, rapid infant weight gain, poor maternal metabolic health, unhealthy diet, and sedentary behavior."
    },
    {
        "query": "How do exosomal microRNAs function as biomarkers for Alzheimer's disease, and which specific miRNAs are most consistently associated with its pathology?",
        "ground_truth": "Exosomal miRNAs are promising biomarkers for Alzheimer's disease due to their stability, tissue specificity, and ability to cross the blood–brain barrier, reflecting key pathological processes such as amyloid-β deposition, tau phosphorylation, and neuroinflammation. Among 120 identified miRNAs, miR-125b, miR-146a, miR-193b, miR-185-5p, miR-29b/c, and miR-21-5p are the most consistently associated with AD."
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