import requests
import json
import time

BASE_URL = "http://localhost:8001/api"

def test():
    # 1. Upload Document A
    print("Uploading Document A...")
    with open("Document_A.pdf", "rb") as f:
        res = requests.post(f"{BASE_URL}/documents/upload", files={"file": f})
        doc_a = res.json()["id"]
        print("Doc A ID:", doc_a)
        
    # 2. Upload Document B
    print("Uploading Document B...")
    with open("Document_B.pdf", "rb") as f:
        res = requests.post(f"{BASE_URL}/documents/upload", files={"file": f})
        doc_b = res.json()["id"]
        print("Doc B ID:", doc_b)
        
    # Wait for processing
    print("Waiting for processing...")
    time.sleep(5)
    
    # 3. Query Doc A only
    print("\n--- Testing Single Query (Doc A) ---")
    res = requests.post(f"{BASE_URL}/chat", json={
        "query": "What is the revenue?",
        "history": [],
        "document_ids": [doc_a]
    }, stream=True)
    
    print("Doc A Response:", end=" ")
    for line in res.iter_lines():
        if line:
            line_str = line.decode('utf-8')
            if line_str.startswith("data: "):
                try:
                    data = json.loads(line_str[6:])
                    if data.get("type") == "chunk":
                        print(data.get("text", ""), end="")
                except:
                    pass
    print()

    # 4. Query Doc B only
    print("\n--- Testing Single Query (Doc B) ---")
    res = requests.post(f"{BASE_URL}/chat", json={
        "query": "What is the revenue?",
        "history": [],
        "document_ids": [doc_b]
    }, stream=True)
    
    print("Doc B Response:", end=" ")
    for line in res.iter_lines():
        if line:
            line_str = line.decode('utf-8')
            if line_str.startswith("data: "):
                try:
                    data = json.loads(line_str[6:])
                    if data.get("type") == "chunk":
                        print(data.get("text", ""), end="")
                except:
                    pass
    print()
    
    # 5. Query Both
    print("\n--- Testing Multi-Document Comparison ---")
    res = requests.post(f"{BASE_URL}/chat", json={
        "query": "Compare the revenue of Document A and Document B.",
        "history": [],
        "document_ids": [doc_a, doc_b]
    }, stream=True)
    
    print("Comparison Response:", end=" ")
    for line in res.iter_lines():
        if line:
            line_str = line.decode('utf-8')
            if line_str.startswith("data: "):
                try:
                    data = json.loads(line_str[6:])
                    if data.get("type") == "chunk":
                        print(data.get("text", ""), end="")
                except:
                    pass
    print()

if __name__ == "__main__":
    test()
