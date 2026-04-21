import json
from ragas import evaluate
from ragas.metrics import(faithfulness,
    answer_relevancy,
    context_precision,
    context_recall)
import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from evaluation.prepare_ragas import convert_to_ragas_format
from langchain_huggingface import HuggingFaceEmbeddings

load_dotenv()

os.getenv("GOOGLE_API_KEY")


def run(data,system_name):
    

    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",  
        temperature=0
    )
    embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)
    ds = convert_to_ragas_format(data,system_name)
    result = evaluate(ds, metrics = [faithfulness,answer_relevancy,context_precision,context_recall], embeddings=embeddings, llm=llm)
    print(result)
    return result

if __name__ == "__main__":
    with open("evaluation/final_data.json") as file:
        data = json.load(file)
    vector_result = run(data,"vector")
    graph_result = run(data,"graph")
    hybrid_result = run(data,"hybrid")
