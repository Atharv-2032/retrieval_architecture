from langchain_core.documents import Document   
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
import time
from collections import Counter

def build_generic_mesh_list(all_papers, threshold=0.25):
    term_counts = Counter()
    total_papers = len(all_papers)

    for paper in all_papers:
        mesh_terms = paper["metadata"].get("mesh_terms", [])
        unique_terms = set(mesh_terms)  # avoid double counting per paper
        term_counts.update(unique_terms)

    generic_terms = {
        term for term, count in term_counts.items()
        if count / total_papers >= threshold
    }

    return generic_terms

def papers_to_embeddings(all_papers,no_of_papers):
    documents = []
    GENERIC_MESH = build_generic_mesh_list(all_papers)
    print("Generic terms: ",GENERIC_MESH)
    for paper in all_papers[:no_of_papers]:
        doc = Document(
            page_content=paper["text"],
            metadata=paper["metadata"]
        )
        documents.append(doc)

    print(f"Total raw documents: {len(documents)}")

    splitter =  RecursiveCharacterTextSplitter(
       chunk_size = 250,
        chunk_overlap = 40
    )

    split_docs = splitter.split_documents(documents)

    #split_docs = documents #for same dataset as graph, as for chroma he took top k out of 20 datasets, while graph took top k out of around a 100

    print(f"Total chunks created: {len(split_docs)}")

    for i, doc in enumerate(split_docs):
        meta = doc.metadata
        mesh_terms = meta.get("mesh_terms", [])

        filtered = [m for m in mesh_terms if m not in GENERIC_MESH]
        
        context = f"Topics: {', '.join(filtered)}."
        doc.page_content = context + " " + doc.page_content

    embeddings = HuggingFaceEmbeddings(
        model_name = "sentence-transformers/all-MiniLM-L6-v2"
    )

    db_path = f"./chroma_db_{int(time.time())}"
    vectorstore = Chroma.from_documents(
        documents=split_docs,
        embedding = embeddings,
        persist_directory=db_path
    )

    vectorstore.persist()

    print("Chroma DB created and saved")


