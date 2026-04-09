def build_prompt(query, retrieved_docs, user_profile, chat_history):

    context = "\n".join(retrieved_docs)
    history = "\n".join(chat_history)

    prompt = f"""
You are a clinical medical assistant helping with patient analysis.

User Profile:
Allergies: {user_profile.get("allergies", [])}
Conditions: {user_profile.get("conditions", [])}
Medical History: {user_profile.get("history", [])}
Family Medical History: {user_profile.get("family_history", [])}
Age: {user_profile.get("age", None)}

Conversation History:
{history}

Relevant Medical Knowledge:
{context}

Current Question:
{query}

Instructions:
- Consider the full conversation history
- Detect contradictions or new information
- Ensure recommendations are safe
- Avoid suggesting contraindicated drugs
- If information conflicts, explain clearly

Answer like a clinical assistant.
"""

    return prompt