import requests
import time

BASE_URL = "http://localhost:8001/api"

print("--- Starting End-to-End Test ---")

# 1. Upload PDF
print("1. Uploading PDF...")
with open("test_doc.pdf", "rb") as f:
    files = {"file": f}
    upload_res = requests.post(f"{BASE_URL}/documents/upload", files=files)

upload_data = upload_res.json()
print("Upload response:", upload_data)
doc_id = upload_data["id"]

# 2. Wait for processing
print("2. Waiting for document to process...")
time.sleep(3) # Give it a bit to chunk and index

# 3. List Documents
print("3. Listing Documents...")
docs_res = requests.get(f"{BASE_URL}/documents")
print("Documents:", docs_res.json())

# 4. Chat - Ask a question that exists
print("4. Asking a question (Revenue)...")
chat_payload_1 = {
    "query": "What was the revenue in 2024?",
    "history": [],
    "document_ids": [doc_id]
}
chat_res_1 = requests.post(f"{BASE_URL}/chat", json=chat_payload_1)
print("Chat Response 1:", chat_res_1.json())

# 5. Chat - Ask a follow-up question
print("5. Asking a follow-up question...")
history = [
    {"role": "user", "content": chat_payload_1["query"]},
    {"role": "assistant", "content": chat_res_1.json()["answer"]}
]
chat_payload_2 = {
    "query": "How many employees are there?",
    "history": history,
    "document_ids": [doc_id]
}
chat_res_2 = requests.post(f"{BASE_URL}/chat", json=chat_payload_2)
print("Chat Response 2:", chat_res_2.json())

# 6. Delete document
print("6. Deleting document...")
del_res = requests.delete(f"{BASE_URL}/documents/{doc_id}")
print("Delete Response:", del_res.json())

print("--- End-to-End Test Complete ---")
