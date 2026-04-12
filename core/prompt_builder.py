def build_prompt(query, retrieved_docs):

    context = "\n".join(retrieved_docs)
    prompt =  f"""
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
    - Use only the provided context
    - Identify relevant entities and relationships
    - Combine information if multiple entries exist
    - Do not use outside knowledge
    - If no relevant information is found, say so clearly

    Answer:
    """
    return prompt

           