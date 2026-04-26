import chromadb
from chromadb.utils import embedding_functions

client = chromadb.PersistentClient(path="./vector_db/chroma_storage")

embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)

collection = client.get_collection(
    name="langchain",
    embedding_function=embedding_function
)

def retrieve(query, k=5):
    results = collection.query(
        query_texts=[query],
        n_results=k
    )
    print(results["documents"][0])

    return results["documents"][0]