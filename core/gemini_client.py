import os
from dotenv import load_dotenv
from google import genai

load_dotenv()
print(os.getenv)
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

def generate_response(prompt):
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )
    return response.text