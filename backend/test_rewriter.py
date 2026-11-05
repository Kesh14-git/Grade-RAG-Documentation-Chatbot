import requests
import json

BASE_URL = "http://localhost:8001/api"

print("--- Testing Query Rewriting ---")

# We will use an existing document if available, or just a dummy document_id 
# since the retrieval might fail but we can still inspect the rewritten query in the response if we implemented it right.
# Wait, if we use a dummy doc_id, hybrid retrieval will just return empty, but RAGService still returns the rewritten query.
# Let's see if we have documents.
docs_res = requests.get(f"{BASE_URL}/documents")
docs = docs_res.json().get("documents", [])
if not docs:
    print("No documents found. Please upload one first.")
    exit(1)
    
doc_id = docs[0]["id"]

tests = [
    {
        "name": "1. Standalone query",
        "query": "What is the dosage of Rinvoq?",
        "history": []
    },
    {
        "name": "2. Pronoun follow-up",
        "query": "What are its side effects?",
        "history": [
            {"role": "user", "content": "What is the dosage of Rinvoq?"},
            {"role": "assistant", "content": "The dosage is 15 mg once daily."}
        ]
    },
    {
        "name": "3. Multi-turn follow-up",
        "query": "Are there any restrictions?",
        "history": [
            {"role": "user", "content": "What is Rinvoq used for?"},
            {"role": "assistant", "content": "Rinvoq is used for rheumatoid arthritis."},
            {"role": "user", "content": "What is the recommended dosage?"},
            {"role": "assistant", "content": "The recommended dosage is 15 mg once daily."}
        ]
    },
    {
        "name": "4. Numerical query",
        "query": "What about 2023?",
        "history": [
            {"role": "user", "content": "What was the revenue in 2024?"},
            {"role": "assistant", "content": "The revenue in 2024 was $10M."}
        ]
    },
    {
        "name": "5. Ambiguous query",
        "query": "Can you elaborate on that?",
        "history": [] # Empty history with ambiguous query -> should just return as is
    }
]

for test in tests:
    print(f"\n{test['name']}")
    print(f"Original Query: {test['query']}")
    payload = {
        "query": test["query"],
        "history": test["history"],
        "document_ids": [doc_id]
    }
    res = requests.post(f"{BASE_URL}/chat", json=payload)
    if res.status_code == 200:
        data = res.json()
        print(f"Rewritten Query: {data.get('rewritten_query')}")
    else:
        print(f"Error: {res.status_code} - {res.text}")

print("\n--- End of Tests ---")
