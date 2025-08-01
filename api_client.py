import requests
import json
import os
from dotenv import load_dotenv
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_API_URL = os.getenv("GEMINI_API_URL")

headers = {
    "Content-Type": "application/json",
    "X-goog-api-key": GEMINI_API_KEY
}

print("GEMINI_API_KEY:", os.getenv("GEMINI_API_KEY"))

payload = {
    "contents": [
        {
            "parts": [
                {
                    "text": "Your transcription text here"
                }
            ]
        }
    ]
}

response = requests.post(GEMINI_API_URL, headers=headers, data=json.dumps(payload))

if response.status_code == 200:
    print("Response:")
    print(json.dumps(response.json(), indent=2))
else:
    print(f"Error: {response.status_code}")
    print(response.text)