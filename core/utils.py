import re
import json


def extract_json(text):

    if not text:
        return {}

  
    match = re.search(r'\{.*?\}', text, re.DOTALL)

    if match:
        try:
            return json.loads(match.group())
        except Exception as e:
            print("[DEBUG] JSON LOAD ERROR:", e)

    print("[DEBUG] No valid JSON found")
    return {}