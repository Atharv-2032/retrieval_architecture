import json

ground_truths = {"explain the Role of Negative Pressure Therapy in Diabetic Foot Ulcer":"Negative Pressure Wound Therapy plays a significant role in the healing of diabetic foot ulcers by accelerating wound healing compared to conventional moist dressings. It promotes earlier formation of granulation tissue, which is essential for wound repair. Additionally, it leads to better overall clinical outcomes, with a higher proportion of complete healing cases (80%) compared to conventional treatment (60%). Therefore, it is an effective therapeutic approach for improving healing rates in diabetic foot ulcers."


}

def add_ground_truth(input_path,output_path):
    with open(input_path) as file:
        data = json.load(file)
    
    for item in data:
        query = item["query"]
        item["ground_truth"] = ground_truths.get(query,"")
    with open(output_path, "w") as file:
        json.dump(data,file,indent=4)
if __name__ == "__main__":
    add_ground_truth("evaluation/clean_data.json","evaluation/final_data.json")