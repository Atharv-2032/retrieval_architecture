def build_prompt(query, retrieved_docs):
    if not retrieved_docs:
        return f"""
    You are a medical research assistant.

    Question:
    {query}

    No context was retrieved from the knowledge base for this query.
    You MUST respond with exactly: "No relevant information found in the knowledge base."
    Do not provide any other information or use outside knowledge.

    Answer:
    """

    context = "\n".join(retrieved_docs)
    
    return f"""
    You are a medical research assistant.

    The context may contain structured medical knowledge including:
    - Diseases
    - Symptoms
    - Treatments
    - Drugs
    - Supporting evidence from research papers

    Context:
    {context}

    Question:
    {query}

    Instructions:
    - Use ONLY the provided context above
    - Do not use outside knowledge
    - Identify relevant entities and relationships
    - Combine information if multiple entries exist
    - If no relevant information is found in the context, say so clearly

    Answer:
    """