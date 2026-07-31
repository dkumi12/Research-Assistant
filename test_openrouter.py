import os
import requests
from dotenv import load_dotenv

load_dotenv()

# Get and clean the key
raw_key = os.getenv("OPENROUTER_API_KEY", "")
clean_key = raw_key.strip().replace("\r", "").replace("\n", "")

print(f"Testing Key: {clean_key[:12]}...")

# Send a raw HTTP request directly to OpenRouter
response = requests.post(
    url="https://openrouter.ai/api/v1/chat/completions",
    headers={
        "Authorization": f"Bearer {clean_key}",
        "Content-Type": "application/json"
    },
    json={
        "model": "google/gemma-4-26b-a4b-it:free", # Using a free model for the test
        "messages": [{"role": "user", "content": "Respond with the word 'Success'."}]
    }
)

print(f"\nStatus Code: {response.status_code}")
print("Response Data:")
print(response.text)