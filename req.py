import requests

response = requests.post(
    "http://localhost:8000/ask",
    json={"query": "What are the penalties for tax evasion?"}
)

print(response.json()["response"])