import json
import os
from datasets import Dataset
from openai import OpenAI
from ragas.llms import llm_factory


from ragas import evaluate
from ragas.metrics import (
    faithfulness,
    answer_relevancy,
    context_precision,
    context_recall
)


from langchain_community.embeddings import HuggingFaceEmbeddings


os.environ["RAGAS_MAX_WORKERS"] = "1"

USE_OPENAI_EMBEDDINGS = False
def load_dataset(path):
    with open(path, "r") as f:
        return Dataset.from_list(json.load(f))


vector_ds = load_dataset("vector_dataset.json")
graph_ds = load_dataset("graph_dataset.json")
hybrid_ds = load_dataset("hybrid_dataset.json")


client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

llm = llm_factory("gpt-4o-mini",client = client)


if USE_OPENAI_EMBEDDINGS:
    from ragas.embeddings import embedding_factory

    embeddings = embedding_factory(
        "text-embedding-3-small",
        client=client
    )
    print("\n Using OpenAI embeddings\n")

else:
    from langchain_community.embeddings import HuggingFaceEmbeddings

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
    print("\n Using HuggingFace embeddings\n")


metrics = [
    faithfulness,
    answer_relevancy,
    context_precision,
    context_recall
]



def run_eval(name, dataset):
    print(f"\n Evaluating {name.upper()}...\n")

    result = evaluate(
        dataset=dataset,
        metrics=metrics,
        llm=llm,
        embeddings=embeddings,
        batch_size = 1,
        raise_exceptions=False
    )

    print(f"{name.upper()} RESULTS:", result)


run_eval("vector", vector_ds)
run_eval("graph", graph_ds)
run_eval("hybrid", hybrid_ds)