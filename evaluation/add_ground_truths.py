import json

ground_truths = {"explain the Role of Negative Pressure Therapy in Diabetic Foot Ulcer":"Negative Pressure Wound Therapy plays a significant role in the healing of diabetic foot ulcers by accelerating wound healing compared to conventional moist dressings. It promotes earlier formation of granulation tissue, which is essential for wound repair. Additionally, it leads to better overall clinical outcomes, with a higher proportion of complete healing cases (80%) compared to conventional treatment (60%). Therefore, it is an effective therapeutic approach for improving healing rates in diabetic foot ulcers.",
                 "Does pre-stroke frailty affect outcomes in patients undergoing reperfusion therapy for acute ischemic stroke?":"Yes. Pre-stroke frailty is associated with significantly increased mortality at both 90 days and one year following reperfusion therapy for acute ischemic stroke. However, it is not associated with a higher risk of symptomatic intracranial hemorrhage or increased post-stroke disability.",
                 "Does green tea kombucha consumption, when combined with an energy-restricted diet, improve cardiometabolic risk markers in individuals with excess body weight?":"Green tea kombucha consumption alongside an energy-restricted diet is associated with improvements in several cardiometabolic risk markers, including reductions in total cholesterol, LDL-c, VLDL-c, triglycerides, and uric acid. However, when compared to an energy-restricted diet alone, there are no significant overall differences between groups, suggesting that while kombucha may provide additional benefits, its effects are not significantly greater than diet alone across the total sample"


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