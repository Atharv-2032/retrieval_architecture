import json


def clean_data(input_path, output_path):
    with open(input_path) as file:
        data = json.load(file)

    cleaned = []

    for item in data:
        valid = True
        for system in ["vector","graph","hybrid"]:
            answer = item[system]["answer"]
            docs = item[system]["retrieved_docs"]

            if not answer or "Error" in answer:
                valid = False
            if not docs or len(docs) == 0:
                valid = False 
        if valid:
            cleaned.append(item)
    print(f"Original: {len(data)}")
    print(f"Cleaned: {len(cleaned)}")

    with open(output_path, "w") as f:
        json.dump(cleaned, f, indent=4)
if __name__ == "__main__":
    clean_data("evaluation/data.json", "evaluation/clean_data.json")
