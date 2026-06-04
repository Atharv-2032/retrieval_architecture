from neo4j import GraphDatabase
import json
import google.generativeai as genai
import spacy

from sentence_transformers import SentenceTransformer, util, CrossEncoder


URI = "bolt://172.30.144.1:7687"
USERNAME = "neo4j"
PASSWORD = "vihangA1@"
driver = GraphDatabase.driver(URI, auth = (USERNAME,PASSWORD))

genai.configure(api_key="AIzaSyC490NYjYgTLo_89r7dTI6H_ApPkdRyjK4")
model = genai.GenerativeModel("gemini-2.5-flash-lite")

filename = "papers_data.json"

#fast-retrieval of top-k sentences
embed_model = SentenceTransformer("all-MiniLM-L6-v2")

#cross-encoder - reranking of retrieved top-k sentences
reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2") 

#splitting abstracts into sentences using scispacy
nlp =  spacy.load("en_core_web_sm")
def split_sentences(text):
    doc = nlp(text)
    return [sent.text.strip() for sent in doc.sents if sent.text.strip()]

def find_context(triplet,sentences):
    triplet_text = f"{triplet['source']} {triplet['relation']} {triplet['target']}"

    if not sentences:
      return ""
    triplet_emb = embed_model.encode(triplet_text,convert_to_tensor=True)
    sent_embs = embed_model.encode(sentences,convert_to_tensor = True)

    scores = util.cos_sim(triplet_emb,sent_embs)[0]

    top_k = min(5,len(sentences))
    top_results = scores.topk(k=top_k)

    candidate_indices = top_results.indices.tolist()
    candidate_sentences = [sentences[i] for i in candidate_indices]

    pairs = [(triplet_text,s) for s in candidate_sentences]
    rerank_scores = reranker.predict(pairs)

    #sort candidates by rerank scores
    ranked = sorted(
        zip(candidate_indices,candidate_sentences,rerank_scores),
        key=lambda x: x[2],
        reverse = True
    )
    selected = []
    used_indices = set()  
    for idx, sentence, score in ranked:
        if idx in used_indices:
            continue

        # pronoun continuity fix
        if sentence.lower().startswith(("it ", "this ", "these ", "they ")) and idx > 0:
            prev = sentences[idx - 1]
            if (idx - 1) not in used_indices:
                selected.append(prev)
                used_indices.add(idx - 1)

        selected.append(sentence)
        used_indices.add(idx)

        if len(selected) >= 2:
            break

    # fallback (just in case)
    if not selected:
        selected.append(candidate_sentences[0])
    
    print("\nTRIPLET:", triplet_text)
    for _, sent, score in ranked:
      print(f"{score:.3f} → {sent}")

    return " ".join(selected[:2])

def find_entity_context(entity_name,sentences):
  if not sentences:
    return ""
  
  query_emb = embed_model.encode(entity_name, convert_to_tensor=True)
  sent_embs = embed_model.encode(sentences, convert_to_tensor=True)

  scores = util.cos_sim(query_emb, sent_embs)[0]

  top_k = min(5, len(sentences))
  top_results = scores.topk(k=top_k)

  candidate_indices = top_results.indices.tolist()
  candidate_sentences = [sentences[i] for i in candidate_indices]

  pairs = [(entity_name, s) for s in candidate_sentences]
  rerank_scores = reranker.predict(pairs)

  ranked = sorted(
      zip(candidate_indices, candidate_sentences, rerank_scores),
      key=lambda x: x[2],
      reverse=True
  )

  selected = []
  used_indices = set()
  
  for idx, sentence, score in ranked:
    if idx in used_indices:
      continue
    
    if sentence.lower().startswith(("it ", "this ", "these ","they ")) and idx > 0:
      prev = sentences[idx-1]
      if(idx - 1) not in used_indices:
        selected.append(prev)
        used_indices.add(idx-1)
      
    selected.append(sentence)
    used_indices.add(idx)

    if len(selected) >= 2:
      break
    
  if not selected:
    selected.append(candidate_sentences[0])
  print("\nENTITY", entity_name)
  for _, sent, score in ranked:
      print(f"{score:.3f} → {sent}")
  return " ".join(selected[:2])
    
      
      
        
try:
    with open(filename,"r",encoding="utf-8") as f:
        all_papers = json.load(f)
        print(f"Successfully loaded {len(all_papers)} papers.")
except FileNotFoundError:
    print("File not found")


def build_prompt2(text):
    return f"""
You are a biomedical information extraction system.

Your task is to extract structured biomedical knowledge as (entity1, relation, entity2) triplets.

---------------------
ENTITY RULES:
---------------------
- Entity types are CLOSED and MUST match EXACTLY one of:

  [Disease, Treatment, Drug, Symptom, RiskFactor]

- Do NOT create new types 
- Do NOT modify type names or casing
- Terms like "biomarker", "marker", "level", "expression", "concentration"
  are NOT valid entity types in this schema
- If such terms appear:
  → map them to RiskFactor IF they indicate increased disease risk
  → otherwise DO NOT extract them as entities

- Keep entity names:
  - concise
  - standardized
  - medically precise
  - avoid long phrases or sentences

- ENTITY NORMALIZATION (VERY IMPORTANT):
  - Expand abbreviations:
    TB → tuberculosis
    COPD → chronic obstructive pulmonary disease
    MI → myocardial infarction
    HTN → hypertension
    DM → diabetes mellitus

  - Prefer FULL medical names over abbreviations
  - Do NOT create multiple variants of the same concept
  - Normalize to the most common clinical term

  Examples:
    "TB" → "tuberculosis"
    "high blood pressure" → "hypertension"
    "high blood sugar" → "diabetes mellitus"

- DO NOT include:
  - generic words like "patients", "study", "increase", "results"
  - vague phrases like "this condition", "these findings"

- If no meaningful biomedical entities are present, return empty lists

---------------------
RELATION RULES (STRICT, KEYWORD-DRIVEN):
---------------------
Valid relations (ONLY these are allowed):

[TREATS, CAUSES, PREVENTS, INTERACTS_WITH, HAS_SYMPTOM, RISK_FACTOR_FOR, AFFECTS, ASSOCIATED_WITH]

- Return relations ONLY by copying EXACTLY from the list above
- Do NOT generate relation names freely
- Do NOT change capitalization
- Do NOT create variants (e.g., "treats", "RiskFactor_FOR" ❌)
- Do NOT use entity types (e.g., "Symptom") as relations


- TREATS:
  Keywords: "treats", "treated with", "therapy", "management of", "improves", "reduces symptoms of"
  Meaning: Drug or treatment improves a disease

- CAUSES:
  Keywords: "causes", "leads to", "results in", "induces", "triggers"
  Meaning: Strong direct causation ONLY

- PREVENTS:
  Keywords: "prevents", "reduces risk of", "protects against", "prophylaxis"
  Meaning: Prevents disease occurrence

- INTERACTS_WITH:
  Keywords: "interacts with", "drug interaction", "metabolized by", "inhibits", "enhances effect of"
  Meaning: Drug-drug or drug-enzyme interaction

- HAS_SYMPTOM:
  Keywords: "symptom", "characterized by", "presents with", "manifested by"
  Meaning: Disease → symptom relationship

- RISK_FACTOR_FOR:
  Keywords: "risk factor", "associated with increased risk", "predisposes", "linked to higher risk"
  Meaning: Factor increases likelihood of disease

- AFFECTS:
  Keywords: "affects", "impacts", "influences", "modulates", "alters"
  Meaning: General biological effect (stronger than ASSOCIATED_WITH)

- ASSOCIATED_WITH (STRICT LIMIT):
  Use ONLY if:
  - a meaningful biomedical relationship is clearly stated
  - AND none of the above categories apply
  - AND the relationship is not weak or vague



---------------------
CRITICAL EXTRACTION RULES:
---------------------

- NEVER default to ASSOCIATED_WITH
- If no strong keyword or clear meaning is present:
  → DO NOT extract a relationship

- It is BETTER to return NO relationship than a weak one

- Only extract relationships with HIGH confidence
- Do NOT infer beyond the text
- Do NOT invent relationships
- source and target MUST be different entities
- NEVER create self-relations (e.g, X -> X)

---------------------
PRIORITY RULES:
---------------------

- ALWAYS try to match a specific relationship first
- Prefer the MOST specific relation if multiple apply
- Use ASSOCIATED_WITH ONLY as a last resort
- Prefer fewer HIGH-QUALITY triplets over many weak ones

---------------------
FINAL VALIDATION:
---------------------

- Remove any entity whose type is not in:
  [Disease, Treatment, Drug, Symptom, RiskFactor]

- If an entity does not fit these types, DO NOT include it

---------------------
OUTPUT FORMAT:
---------------------

Return ONLY valid JSON in the following format:

{{
  "entities": [
    {{"name": "...", "type": "..."}}
  ],
  "relationships": [
    {{"source": "...", "relation": "...", "target": "..."}}
  ]
}}

---------------------
TEXT:
---------------------
{text}
"""

def extract_graph(text):
    prompt = build_prompt2(text)

    response = model.generate_content(
        prompt,
        generation_config={"response_mime_type":"application/json"}
        )
    response = response.text
    data = json.loads(response)
    return data

def insert_graph(tx,data,metadata):
    #create paper node
    tx.run(
        """
        MERGE (p:Paper {doc_id: $doc_id})
        SET p.title = $title
        """,
        doc_id = metadata["doc_id"],
        title = metadata["title"]
    )

    #create entities + MENTIONS
    for entity in data["entities"]:
        tx.run(
            f"MERGE (n:{entity['type']} {{name: $name}})",
            name=entity["name"]
        )

        context = entity.get("context", "")   

        #link entity to paper
        tx.run(
            f"""
            MATCH (p:Paper {{doc_id: $doc_id}})
            MATCH (n:{entity['type']} {{name: $name}})
            MERGE (p)-[r:MENTIONS]->(n)
            SET r.context = $context
            """,
            doc_id=metadata["doc_id"],
            name=entity["name"],
            context = context
        )
    # Link entity to entity
    for rel in data["relationships"]:
        tx.run(
            f"""
            MATCH (a {{name: $source}})
            MATCH (b {{name: $target}})
            MERGE (a)-[r:{rel['relation']}]->(b)
            SET r.context = $context, 
                r.doc_id = $doc_id
            """,
            source=rel["source"],
            target=rel["target"],
            context = rel["context"],
            doc_id = metadata["doc_id"]
        )



def main():
    for i,paper in enumerate(all_papers):
        text= paper["text"]
        sentences = split_sentences(text)
        metadata = paper["metadata"]

        print(f"\nProcessing paper {i+1}: {metadata['title']}")

        try:
            data = extract_graph(text)

            #FOR EACH ENTITY, FIND TOP SENTENCES, AND PUT THAT AS CONTEXT FOR MENTIONS RELATIONSHIP, INSTEAD OF TREATING MENTIONS AS TRIPLETS
            for entity in data["entities"]:
              entity["context"] = find_entity_context(entity["name"],sentences)

            #add context for each relationship
            for rel in data["relationships"]:
                rel["context"] = find_context(rel,sentences) #these are all LLM generated relationships
            
            with driver.session() as session:
                session.execute_write(insert_graph,data,metadata)
            
            

        
        except Exception as e:
            print("Error:",e)
            continue
    print("\nAll papers processed")
    driver.close()


if __name__ == "__main__":
    main()
    driver.close()
