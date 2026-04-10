import chromadb

client = chromadb.PersistentClient(path="./vector_db/chroma_storage")

print(client.list_collections())