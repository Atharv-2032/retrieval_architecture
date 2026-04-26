import json


def graph_to_text(doc: str) -> str:
    return doc.replace("\n", ". ")


def build_datasets(data):
    vector_data, graph_data, hybrid_data = [], [], []

    for row in data:

       
        vector_answer = row["vector"].get("answer", "").strip()
        if not vector_answer:
            print(f"[WARNING] Empty VECTOR answer → {row['query']}")

        vector_contexts = row["vector"].get("retrieved_docs", [])
        if not vector_contexts:
            print(f"[WARNING] Empty VECTOR contexts → {row['query']}")

        vector_data.append({
            "question": row["query"],
            "answer": vector_answer,
            "contexts": vector_contexts,
            "ground_truth": row["ground_truth"]
        })


        
        graph_answer = row["graph"].get("answer", "").strip()
        if not graph_answer:
            print(f"[WARNING] Empty GRAPH answer → {row['query']}")

        graph_contexts = [
            graph_to_text(doc)
            for doc in row["graph"].get("retrieved_docs", [])
            if doc.strip()
        ]

        if not graph_contexts:
            print(f"[WARNING] Empty GRAPH contexts → {row['query']}")

        graph_data.append({
            "question": row["query"],
            "answer": graph_answer,
            "contexts": graph_contexts,
            "ground_truth": row["ground_truth"]
        })


        hybrid_answer = row["hybrid"].get("answer", "").strip()
        if not hybrid_answer:
            print(f"[WARNING] Empty HYBRID answer → {row['query']}")

        hybrid_contexts = row["hybrid"].get("retrieved_docs", [])
        if not hybrid_contexts:
            print(f"[WARNING] Empty HYBRID contexts → {row['query']}")

        hybrid_data.append({
            "question": row["query"],
            "answer": hybrid_answer,
            "contexts": hybrid_contexts,
            "ground_truth": row["ground_truth"]
        })

    return vector_data, graph_data, hybrid_data


def validate(data, name):
    for i, row in enumerate(data):
        if not isinstance(row["contexts"], list):
            raise ValueError(f"{name} row {i}: contexts not list")

        if len(row["contexts"]) == 0:
            raise ValueError(f"{name} row {i}: empty contexts")

        if not isinstance(row["ground_truth"], str):
            raise ValueError(f"{name} row {i}: missing ground truth")



with open("ragas_input.json", "r") as f:
    data = json.load(f)

vector_data, graph_data, hybrid_data = build_datasets(data)

validate(vector_data, "vector")
validate(graph_data, "graph")
validate(hybrid_data, "hybrid")


# -----------------------------
# 💾 SAVE DATASETS
# -----------------------------
with open("vector_dataset.json", "w") as f:
    json.dump(vector_data, f, indent=2)

with open("graph_dataset.json", "w") as f:
    json.dump(graph_data, f, indent=2)

with open("hybrid_dataset.json", "w") as f:
    json.dump(hybrid_data, f, indent=2)


print("\n Datasets built and saved!")