from hybrid.extract_entity_from_vector import extract_entities_from_docs
from hybrid.match_entities import match_entities
from hybrid.selected_paths import select_traversal_paths
from hybrid.traverse_graph import traverse_graph

# -------------------------------
# Sample vector docs
# -------------------------------
docs = [
    "Reperfusion therapy such as thrombectomy is used in stroke patients.",
    "Stroke is associated with dizziness and requires early treatment."
]


# -------------------------------
# STEP 1: Extract entities
# -------------------------------
entities = extract_entities_from_docs(docs)
print("\n[STEP 1] Extracted Entities:")
print(entities)


# -------------------------------
# STEP 2: Match entities to graph
# -------------------------------
matches = match_entities(entities)
print("\n[STEP 2] Matched Graph Nodes:")
print(matches)


# -------------------------------
# STEP 3: LLM selects traversal paths
# -------------------------------
query = "What causes dizziness?"

paths = select_traversal_paths(query, matches)
print("\n[STEP 3] Selected Traversal Paths:")
print(paths)



graph_results = traverse_graph(matches, paths)

print("\n[STEP 4] Graph Traversal Results:")
print(graph_results)