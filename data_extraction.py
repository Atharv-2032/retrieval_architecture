from Bio import Entrez
import time
from http.client import IncompleteRead

from vector_embeddings import papers_to_embeddings
from extract_json_data import papers_to_json

import os
from dotenv import load_dotenv
#from llm_to_graph import papers_to_graph

load_dotenv()

def safe_efetch(ids,max_retries = 5):
    for attempt in range(max_retries):
        try:
            handle = Entrez.efetch(
                db = "pubmed",
                id = ids,
                retmode="xml"
            )
            records = Entrez.read(handle)
            handle.close()
            return records
        except (IncompleteRead,Exception) as e:
            wait_time = 2 ** attempt  # exponential backoff
            print(f"efetch failed (attempt {attempt+1}): {e}")
            print(f"Retrying in {wait_time}s...")
            time.sleep(wait_time)
    print("efetch failed after retries. Skipping this query")

Entrez.email = os.getenv("ENTREZ_EMAIL")
Entrez.api_key = os.getenv("ENTREZ_API_KEY")

queries = [
    '(infectious disease*[Title/Abstract] OR infection*[Title/Abstract]) AND (therapy[Title/Abstract] OR treatment[Title/Abstract]) AND "Humans"[MeSH Terms]',
    '("Cardiovascular Diseases"[MeSH Terms]) AND (treatment[Title/Abstract] OR therapy[Title/Abstract]) AND "Humans"[MeSH Terms]',
    '("Neoplasms"[MeSH Terms]) AND (therapy[Title/Abstract] OR treatment[Title/Abstract]) AND "Humans"[MeSH Terms]',
    '("Nervous System Diseases"[MeSH Terms]) AND (treatment[Title/Abstract] OR therapy[Title/Abstract]) AND "Humans"[MeSH Terms]',
    '("Diabetes Mellitus"[MeSH Terms]) AND (treatment[Title/Abstract] OR therapy[Title/Abstract]) AND "Humans"[MeSH Terms]',
    '("Drug Interactions"[MeSH Terms]) AND (adverse effects[Title/Abstract]) AND "Humans"[MeSH Terms]',
    '("Immune System Diseases"[MeSH Terms]) AND (treatment[Title/Abstract] OR therapy[Title/Abstract]) AND "Humans"[MeSH Terms]',
    '("Lung Diseases"[MeSH Terms]) AND (treatment[Title/Abstract] OR therapy[Title/Abstract]) AND "Humans"[MeSH Terms]',
    '("Digestive System Diseases"[MeSH Terms]) AND (treatment[Title/Abstract] OR therapy[Title/Abstract]) AND "Humans"[MeSH Terms]',
    '("Mental Disorders"[MeSH Terms]) AND (therapy[Title/Abstract] OR treatment[Title/Abstract]) AND "Humans"[MeSH Terms]',

    '("Vaccination"[MeSH Terms]) AND (disease prevention[Title/Abstract])',
    '("Preventive Health Services"[MeSH Terms]) AND humans',
    '(drug therapy[Title/Abstract]) AND "Humans"[MeSH Terms]',
    '("Drug Interactions"[MeSH Terms]) AND "Humans"[MeSH Terms]',
    '("Drug Resistance"[MeSH Terms]) AND (treatment[Title/Abstract] OR therapy[Title/Abstract]) AND "Humans"[MeSH Terms]',
    '("Pharmaceutical Preparations"[MeSH Terms]) AND (clinical trial[Title/Abstract]) AND "Humans"[MeSH Terms]',
    '("Treatment Outcome"[MeSH Terms]) AND (therapy[Title/Abstract] OR treatment[Title/Abstract]) AND "Humans"[MeSH Terms]',

    '(symptoms OR "clinical presentation" OR "presents with")[Title/Abstract] AND disease',
    '("Disease Attributes"[MeSH Terms]) AND symptom',
    '("Diagnosis"[MeSH Terms]) AND (methods[Title/Abstract]) AND "Humans"[MeSH Terms]',
    '("Diagnostic Techniques and Procedures"[MeSH Terms]) AND (disease OR disorder OR condition)[Title/Abstract]',
    '("Biomarkers"[MeSH Terms]) AND (disease OR disorder OR condition)[Title/Abstract]',

    '("Risk Factors"[MeSH Terms]) AND (disease OR disorder OR condition)[Title/Abstract]',
    '("Comorbidity"[MeSH Terms]) AND "Humans"[MeSH Terms]',
    '("Disease Progression"[MeSH Terms]) AND "Humans"[MeSH Terms]',
    '("Epidemiology"[MeSH Terms]) AND (disease OR disorder OR condition)[Title/Abstract]',

    '(pathophysiology OR mechanism OR "disease mechanism")[Title/Abstract]',
    '("Inflammation"[MeSH Terms]) AND (disease OR disorder OR condition)[Title/Abstract]',
    '("Immune Response"[MeSH Terms] OR immune response[Title/Abstract])'

]

queries_less = [
    '("Diabetes Mellitus, Type 2"[MeSH Terms]) AND (treatment OR therapy OR risk OR complications)',
    '("Cardiovascular Diseases"[MeSH Terms]) AND (treatment OR risk OR prevention)',
    '("Depressive Disorder"[MeSH Terms]) AND (therapy OR treatment OR symptoms)',
    '("Asthma"[MeSH Terms]) AND (treatment OR therapy OR risk OR symptoms)',
    '("Lung Neoplasms"[MeSH Terms]) AND (therapy OR treatment OR biomarkers OR risk)'
]

VALID_TYPES = [
    "Randomized Controlled Trial",
    "Clinical Trial", #apparently clinical trials introduce noisy conclusions and weaker evidence chains
    "Meta-Analysis",
    "Systematic Review",
]

TOP_K_PER_QUERY = 20 #rn we arent hitting this no for almost  all topics, either increase no of papers, or reduce filter strictness





all_papers = []
doc_id = 0
seen_ids = set()
best_papers = {}
retmax_val = 300
for query in queries_less:
    print(f"\nProcessing query: {query}")
    query_papers = []

    handle = Entrez.esearch(db="pubmed", term=query, retmax=retmax_val)
    record = Entrez.read(handle)
    ids = record["IdList"]
    print(record['Count'])
    #print(record["IdList"])
    records = safe_efetch(ids)
    time.sleep(2)
    if records is None:
        continue
    
    for article in records["PubmedArticle"]:
        try:
            medline = article["MedlineCitation"]
            pmid = str(medline["PMID"])
            article_data = medline["Article"]

            title = article_data.get("ArticleTitle", "")
            title_key = title.lower().strip()
            dedup_key = pmid if pmid else title_key


            if "Abstract" not in article_data:
                continue

            text = " ".join(article_data["Abstract"]["AbstractText"])
            if len(text) < 100:
                continue

            try:
                year = int(article_data["Journal"]["JournalIssue"]["PubDate"]["Year"])
            except:
                year = None

            if year and year < 2012:
                continue

            journal = article_data["Journal"]["Title"]
            pub_types = [str(pt) for pt in article_data.get("PublicationTypeList", [])]

            if not any(pt in VALID_TYPES for pt in pub_types):
                continue

            mesh_terms = []
            if "MeshHeadingList" in medline:
                for mesh in medline["MeshHeadingList"]:
                    mesh_terms.append(str(mesh["DescriptorName"]))
            else: 
                continue
            print(mesh_terms)

            # -------- Scoring --------
            score = 0

            if "Randomized Controlled Trial" in pub_types:
                score += 3
            elif "Meta-Analysis" in pub_types or "Systematic Review" in pub_types:
                score += 3
            elif "Clinical Trial" in pub_types:
                score += 2

            for term in mesh_terms:
                if term.lower() in query.lower():
                    score += 2
                    break

            if year and year >= 2020:
                score += 1

            query_papers.append({
                "text": text,
                "metadata": {
                    "pmid" : pmid,
                    "source": "pubmed",
                    "title": title,
                    "query": query,
                    "year": year,
                    "journal": journal,
                    "publication_types": pub_types,
                    "mesh_terms": mesh_terms,
                    "doc_id": doc_id,
                    "score": score
                }
            })


            doc_id += 1
            print(query_papers["metadata"])
        except:
            continue


    query_papers = sorted(query_papers, key=lambda x: x["metadata"]["score"], reverse=True)
    top_k_papers = query_papers[:TOP_K_PER_QUERY]

    print(f"Top-K before dedup: {len(top_k_papers)}")

    for paper in top_k_papers:
        pmid = paper["metadata"].get("pmid")
        title_key = paper["metadata"]["title"].lower().strip()

        key = pmid if pmid else title_key
        score = paper["metadata"]["score"]

        if key not in best_papers or score > best_papers[key]["metadata"]["score"]:
            best_papers[key] = paper

    print(f"Total unique papers so far: {len(best_papers)}")

    time.sleep(1)

all_papers = list(best_papers.values())
print(f"\nTotal final papers: {len(all_papers)}")

papers_to_embeddings(all_papers,200)
papers_to_json(all_papers,200)


