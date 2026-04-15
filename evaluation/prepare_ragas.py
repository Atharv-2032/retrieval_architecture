import json
from datasets import Dataset

import json
from datasets import Dataset


def convert_to_ragas_format(data, system):
    ragas_data = []

    for item in data:
        ragas_data.append({
            "question": item["query"],
            "answer": item[system]["answer"],
            "contexts": item[system]["retrieved_docs"],
            "ground_truth": item["ground_truth"]
        })

    return Dataset.from_list(ragas_data)


if __name__ == "__main__":

    with open("evaluation/final_data.json") as f:
        data = json.load(f)

   
   
    vector_ds = convert_to_ragas_format(data, "vector")
    graph_ds = convert_to_ragas_format(data, "graph")
    #hybrid_ds = convert_to_ragas_format(data, "hybrid")

    print(" Datasets ready")

    vector_ds.to_json("evaluation/vector_ragas.json")
    graph_ds.to_json("evaluation/graph_ragas.json")
    #hybrid_ds.to_json("evaluation/hybrid_ragas.json")