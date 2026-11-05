import requests
import json
import time
import os

BASE_URL = "http://localhost:8001/api"

def upload_docs():
    # Use existing Document_A and Document_B
    print("Uploading Document A...")
    with open("Document_A.pdf", "rb") as f:
        res = requests.post(f"{BASE_URL}/documents/upload", files={"file": f})
        doc_a = res.json()["id"]
        
    print("Uploading Document B...")
    with open("Document_B.pdf", "rb") as f:
        res = requests.post(f"{BASE_URL}/documents/upload", files={"file": f})
        doc_b = res.json()["id"]
        
    print("Waiting for indexing to complete (including BGE-M3)...")
    time.sleep(15) # Wait a bit longer for multilingual indexing
    return doc_a, doc_b

def query_system(query, doc_ids=None, lang="Auto"):
    print(f"\n[Query]: {query}")
    print(f"[Docs]: {doc_ids}")
    print(f"[Resp Lang]: {lang}")
    
    payload = {
        "query": query,
        "history": [],
        "document_ids": doc_ids,
        "response_language": lang
    }
    
    res = requests.post(f"{BASE_URL}/chat", json=payload, stream=True)
    
    print("[Answer]: ", end="")
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
    print("\n-------------------------")

if __name__ == "__main__":
    if not os.path.exists("Document_A.pdf"):
        print("Please run create_multi_docs.py first")
        exit(1)
        
    doc_a, doc_b = upload_docs()
    
    # 1. Baseline English
    query_system("What is the revenue for Document A?", [doc_a], "English")
    
    # 2. Tamil Query (Cross-lingual retrieval) against Document B
    query_system("வருவாய் எவ்வளவு?", [doc_b], "Tamil")
    
    # 3. Hindi Query (Cross-lingual retrieval) against Both Documents
    query_system("राजस्व कितना है?", [doc_a, doc_b], "Hindi")
    
    # 4. Mixed language
    query_system("2024-ல் Document A-யின் revenue என்ன?", [doc_a], "Auto")
