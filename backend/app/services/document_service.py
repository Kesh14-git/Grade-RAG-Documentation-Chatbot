import json
import os
from typing import List, Dict, Any

class DocumentService:
    def __init__(self, storage_path: str = "./documents_meta.json"):
        self.storage_path = storage_path
        self.documents: Dict[str, Dict[str, Any]] = {}
        self.load_documents()

    def load_documents(self):
        if os.path.exists(self.storage_path):
            with open(self.storage_path, "r") as f:
                self.documents = json.load(f)
        else:
            self.documents = {}

    def save_documents(self):
        with open(self.storage_path, "w") as f:
            json.dump(self.documents, f)

    def add_document(self, doc_id: str, filename: str):
        self.documents[doc_id] = {
            "id": doc_id,
            "filename": filename,
            "status": "processing"
        }
        self.save_documents()

    def update_status(self, doc_id: str, status: str):
        if doc_id in self.documents:
            self.documents[doc_id]["status"] = status
            self.save_documents()

    def get_documents(self) -> List[Dict[str, Any]]:
        return list(self.documents.values())

    def delete_document(self, doc_id: str):
        if doc_id in self.documents:
            del self.documents[doc_id]
            self.save_documents()

document_service = DocumentService()
