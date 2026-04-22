import json
import time
from graph.run_graph import run_graph_query
from vector.run_vector import run_vector_query
from hybrid.run_hybrid import run_hybrid_query

def collect_data(queries):
    results = []
    for q in queries:
        try:
            vector_ans = run_vector_query(q)
            time.sleep(2)

            graph_ans = run_graph_query(q)
            time.sleep(2)

            hybrid_ans = run_hybrid_query(q)
            time.sleep(2)

            

            results.append({
                "query":q,
                "vector": vector_ans,
                "graph": graph_ans,
                "hybrid": hybrid_ans
                
            })
        except Exception as e:
            print("failed: ",e)
        time.sleep(2)
    with open("evaluation/data.json","w") as file:
        json.dump(results,file,indent = 4)

if __name__ == "__main__":
    queries = [
        "explain the Role of Negative Pressure Therapy in Diabetic Foot Ulcer",
        "Does pre-stroke frailty affect outcomes in patients undergoing reperfusion therapy for acute ischemic stroke?",
        "Does green tea kombucha consumption, when combined with an energy-restricted diet, improve cardiometabolic risk markers in individuals with excess body weight?"

        
    ]
    collect_data(queries)