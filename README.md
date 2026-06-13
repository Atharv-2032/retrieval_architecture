# HealthRAG

**A Comparative Study of Vector, Graph, and Hybrid Retrieval-Augmented Generation Architectures for Biomedical Question Answering**

HealthRAG builds three RAG pipelines over the same biomedical corpus and evaluates them head-to-head using RAGAS metrics. The goal is a clean, reproducible comparison — same data, same LLM, different retrieval strategies.

---

## Results

| Architecture | Faithfulness | Answer Relevancy | Context Precision | Context Recall |
|---|---|---|---|---|
| Vector RAG | 0.9158 | 0.7156 | 0.7129 | 0.7922 |
| Graph RAG | 0.9189 | 0.6047 | 0.4573 | 0.6111 |
| **Hybrid RAG** | **0.9031** | **0.7132** | **0.6875** | **0.7455** |

Averaged across 3 independent runs on a 60-question benchmark (22 single-hop, 24 multi-hop, 14 aggregative).

---

## Architecture Overview

```
PubMed (91 papers)
       │
       ▼
Data Pipeline (filter → score → deduplicate)
       │
       ├──────────────────────┐
       ▼                      ▼
Chroma Vector DB          Neo4j Knowledge Graph
(chunked abstracts         (666 nodes, 1286
 + MeSH embeddings)        context-enriched edges)
       │                      │
       └──────────┬───────────┘
                  ▼
     ┌────────────┼────────────┐
     ▼            ▼            ▼
Vector RAG    Graph RAG    Hybrid RAG
     │            │            │
     └────────────┼────────────┘
                  ▼
           Gemini API (answer generation)
                  ▼
           RAGAS Evaluation
```

### Vector RAG
Embeds the query → cosine search over Chroma → top-k chunks → Gemini.

### Graph RAG
Extracts entities from query → LLM selects traversal paths → scored node matching in Neo4j → 3-hop traversal collecting edge contexts → Gemini.

### Hybrid RAG
Vector retrieval first → entities extracted from retrieved chunks (not raw query) → graph traversal → top 4 vector + top 4 graph contexts merged → Gemini.

---

## Knowledge Graph

| Node Label | Count |
|---|---|
| Disease | 184 |
| Treatment | 113 |
| RiskFactor | 106 |
| Paper | 91 |
| Symptom | 90 |
| Drug | 82 |

Relationships: `TREATS`, `CAUSES`, `HAS_SYMPTOM`, `RISK_FACTOR_FOR`, `PREVENTS`, `INTERACTS_WITH`, `AFFECTS`, `ASSOCIATED_WITH`, `MENTIONS`

Each relationship stores a `context` property — the supporting sentence from the source abstract — retrieved using bi-encoder candidate selection followed by cross-encoder reranking.

---

## Project Structure

```
retrieval_architecture_research/
├── core/
│   ├── gemini_client.py        # Gemini API wrapper
│   ├── graph_state.py          # LangGraph shared state schema
│   ├── common_nodes.py         # shared prompt + LLM nodes
│   └── utils.py                # normalize_entity, extract_json
│
├── data/
│   ├── fetch_papers.py         # PubMed retrieval via Entrez API
│   ├── filter_papers.py        # 5-stage quality filter + scoring
│   └── build_corpus.py         # deduplication + final corpus
│
├── vector/
│   ├── embed.py                # chunk, inject MeSH prefix, embed
│   ├── store.py                # Chroma DB management
│   └── retrieve.py             # cosine similarity retrieval
│
├── graph/
│   ├── build_graph.py          # LLM triplet extraction + Neo4j ingestion
│   ├── context_enrichment.py   # bi-encoder + cross-encoder pipeline
│   ├── extract_entity.py       # query entity extraction
│   ├── select_paths.py         # rule-based pre-filter + LLM path selection
│   ├── retrieve_graph.py       # scored node matching + traversal
│   └── neo4j_client.py         # Neo4j driver wrapper
│
├── hybrid/
│   ├── extract_entity_from_vector.py
│   ├── match_entities.py
│   ├── selected_paths.py
│   ├── traverse_graph.py
│   └── hybrid_nodes.py
│
├── evaluation/
│   ├── generate_questions.py   # benchmark generation from graph
│   ├── run_evaluation.py       # RAGAS evaluation runner
│   └── question_set.json       # 60-question benchmark
│
├── run_vector.py
├── run_graph.py
├── run_hybrid.py
└── app.py                      # Streamlit interface
```

---

## Setup

### Prerequisites

- Python 3.12
- Neo4j (Community Edition, running locally or via Docker)
- A Google Gemini API key

### Installation

```bash
git clone https://github.com/Atharv-2032/HealthRAG.git
cd HealthRAG
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Environment variables

Create a `.env` file in the project root:

```env
GEMINI_API_KEY=your_gemini_api_key_here
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_neo4j_password
```

### Neo4j setup

Start Neo4j and note the bolt URI, username, and password. Update `graph/neo4j_client.py` or the `.env` file accordingly.

---

## Running the Pipelines

### 1. Build the corpus

```bash
python data/fetch_papers.py       # retrieve from PubMed
python data/filter_papers.py      # filter, score, deduplicate
```

### 2. Build the vector store

```bash
python vector/embed.py            # chunks + MeSH prefix + embeddings → Chroma
```

### 3. Build the knowledge graph

```bash
python graph/build_graph.py       # LLM extraction + context enrichment → Neo4j
```

### 4. Run a pipeline

```bash
python run_vector.py              # Vector RAG
python run_graph.py               # Graph RAG
python run_hybrid.py              # Hybrid RAG
```

### 5. Launch the Streamlit interface

```bash
streamlit run app.py
```

### 6. Run evaluation

```bash
python evaluation/run_evaluation.py
```

---

## Evaluation Benchmark

The 60-question benchmark was generated directly from the Neo4j graph — each question is grounded in an actual relationship and has a traceable ground truth. Questions span three complexity levels:

- **Single-hop (22)** — answerable from one relationship context
- **Multi-hop (24)** — require chaining two relationships
- **Aggregative (14)** — require combining multiple relationships on the same node

---

## Key Implementation Notes

- **Entity normalisation** preserves hyphens (`[^a-z0-9\s\-]` regex) — critical for matching hyphenated biomedical terms like `glucagon-like peptide-1 receptor agonists`
- **MENTIONS always appended** to selected graph paths — Paper nodes only connect via MENTIONS so it must always be traversable
- **Hard-gated prompt** — when retrieved docs are empty the LLM is given a single permissible response, preventing hallucination
- **Cypher null filtering** uses list comprehension before `UNWIND` — `WHERE` after `UNWIND` is invalid Cypher syntax

---

## Tech Stack

| Component | Tool |
|---|---|
| LLM | Google Gemini API |
| Vector DB | ChromaDB |
| Graph DB | Neo4j |
| Embeddings | Sentence Transformers (MiniLM) |
| Reranking | Cross-encoder (Sentence Transformers) |
| Orchestration | LangGraph |
| PubMed API | BioPython Entrez |
| Evaluation | RAGAS |
| UI | Streamlit |

---

## Authors

Atharv Gupta · Ishan Kelkar 

Department of Information Science and Engineering
Ramaiah Institute of Technology, Bengaluru
Mini Project ISP67 — 2025-26
