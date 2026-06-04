import json

def papers_to_json(all_papers,no_of_papers):
    with open("papers_data.json","w",encoding="utf-8") as f:
        json.dump(all_papers[:no_of_papers], f, indent = 4, ensure_ascii = False)

    print(f"Successfully saved {len(all_papers)} papers to papers_data.json")