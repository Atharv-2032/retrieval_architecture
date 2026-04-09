import chromadb
from chromadb.utils import embedding_functions

client = chromadb.PersistentClient(path="./vector_db/chroma_storage")

embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)

collection = client.get_or_create_collection(
    name="medical_collection",
    embedding_function=embedding_function
)

documents = [
    "Aspirin is used for pain relief but is contraindicated in patients with aspirin allergy.",
    "Paracetamol is preferred for pain management in patients with aspirin allergy.",
    "NSAIDs like ibuprofen can cause gastric irritation and should be avoided in patients with ulcers.",
    "Hypertension increases the risk of stroke and cardiovascular disease.",
    "Patients with hypertension should avoid medications that increase blood pressure.",
    "Chronic headaches in elderly patients may be linked to hypertension or vascular issues.",
    "Family history of diabetes increases risk of developing diabetes.",
    "Elderly patients require lower dosages due to reduced metabolic function.",
    "Patients with gastric sensitivity should avoid NSAIDs.",
    "Stroke risk is higher in patients with hypertension and family history of stroke.",
    "Dizziness may be caused by blood pressure fluctuations or neurological conditions.",
    "Drug interactions must be considered when treating patients with multiple conditions."
]

collection.add(
    documents=documents,
    ids=[f"id{i}" for i in range(len(documents))]
)

print("Database created successfully")