import os
from dotenv import load_dotenv
from google import genai
import time

load_dotenv()
print(os.getenv)
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

def generate_response(prompt):
    time.sleep(5)
    response = client.models.generate_content(

        model="gemini-2.5-flash",
        contents=prompt
        
    )
    return response.text



