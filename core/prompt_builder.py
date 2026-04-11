def build_prompt(query, retrieved_docs):

    context = "\n".join(retrieved_docs)
    

    prompt =  f"""
You are a medical research assistant.

Use the structured knowledge below to answer.

Context:
{context}

Question:
{query}

Answer clearly and base it only on the provided context.

Instructions:
- Detect contradictions or new information
- Ensure recommendations are safe
- Avoid suggesting contraindicated drugs
- If information conflicts, explain clearly


"""

    return prompt