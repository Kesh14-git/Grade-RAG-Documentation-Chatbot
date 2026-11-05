import json
import os
from rank_bm25 import BM25Okapi
from typing import List, Dict, Any

class BM25Store:
    def __init__(self, storage_path: str = "./bm25_corpus.json"):
        self.storage_path = storage_path
        self.corpus_data: List[Dict[str, Any]] = []
        self.bm25: BM25Okapi = None
        self.load_corpus()

    def load_corpus(self):
        if os.path.exists(self.storage_path):
            with open(self.storage_path, "r") as f:
                self.corpus_data = json.load(f)
            self._rebuild_index()
        else:
            self.corpus_data = []
            self.bm25 = None

    def save_corpus(self):
        with open(self.storage_path, "w") as f:
            json.dump(self.corpus_data, f)

    def _tokenize(self, text: str) -> List[str]:
        # Basic tokenization: lowercase and split by whitespace
        return text.lower().split()

    def _rebuild_index(self):
        if not self.corpus_data:
            self.bm25 = None
            return
        
        tokenized_corpus = [self._tokenize(doc["content"]) for doc in self.corpus_data]
        self.bm25 = BM25Okapi(tokenized_corpus)

    def add_documents(self, chunks: List[Dict[str, Any]]):
        if not chunks:
            return
        # Avoid duplicates based on chunk_id
        existing_ids = {doc["chunk_id"] for doc in self.corpus_data}
        for chunk in chunks:
            if chunk["chunk_id"] not in existing_ids:
                # Ensure we store metadata
                self.corpus_data.append({
                    "chunk_id": chunk["chunk_id"],
                    "content": chunk["content"],
                    "metadata": {
                        "document_id": chunk["document_id"],
                        "document_name": chunk["document_name"],
                        "page_number": chunk.get("page_number", 1)
                    }
                })
        self.save_corpus()
        self._rebuild_index()

    def delete_document(self, document_id: str):
        self.corpus_data = [doc for doc in self.corpus_data if doc["metadata"]["document_id"] != str(document_id)]
        self.save_corpus()
        self._rebuild_index()

    def search(self, query: str, top_k: int = 10, filter_dict: dict = None) -> List[Dict[str, Any]]:
        if not self.bm25 or not self.corpus_data:
            return []
            
        tokenized_query = self._tokenize(query)
        scores = self.bm25.get_scores(tokenized_query)
        
        # Pair scores with docs
        scored_docs = list(zip(scores, self.corpus_data))
        
        # Apply filter if any
        if filter_dict and "document_id" in filter_dict:
            doc_filter = filter_dict["document_id"]
            if isinstance(doc_filter, dict) and "$in" in doc_filter:
                valid_ids = set(doc_filter["$in"])
                scored_docs = [sd for sd in scored_docs if sd[1]["metadata"].get("document_id") in valid_ids]
            else:
                scored_docs = [sd for sd in scored_docs if sd[1]["metadata"].get("document_id") == doc_filter]
            
        # Sort by score descending
        scored_docs.sort(key=lambda x: x[0], reverse=True)
        
        output = []
        for score, doc in scored_docs[:top_k]:
            if score > 0: # Only return matching docs
                output.append({
                    "chunk_id": doc["chunk_id"],
                    "content": doc["content"],
                    "metadata": doc["metadata"],
                    "score": score
                })
        return output

bm25_store = BM25Store()
