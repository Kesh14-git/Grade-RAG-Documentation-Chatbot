import chromadb
from chromadb.config import Settings
from app.config import settings
from typing import List, Dict, Any

class VectorStore:
    def __init__(self, collection_name="documents"):
        # We use PersistentClient so data survives restarts
        self.client = chromadb.PersistentClient(path=settings.VECTOR_STORE_PATH)
        # Using default L2 distance.
        self.collection = self.client.get_or_create_collection(name=collection_name)

    def add_documents(self, chunks: List[Dict[str, Any]], embeddings: List[List[float]]):
        """
        Add chunks and their embeddings to ChromaDB.
        """
        if not chunks:
            return
            
        ids = [chunk["chunk_id"] for chunk in chunks]
        documents = [chunk["content"] for chunk in chunks]
        
        # Metadata must be strings, ints, floats, or bools
        metadatas = []
        for chunk in chunks:
            meta = {
                "document_id": str(chunk["document_id"]),
                "document_name": str(chunk["document_name"]),
                "page_number": int(chunk.get("page_number", 1))
            }
            if "base64_images" in chunk and chunk["base64_images"]:
                # ChromaDB only accepts int, float, bool, or str in metadata.
                meta["base64_image"] = chunk["base64_images"][0]
                
            metadatas.append(meta)
            
        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas
        )

    def search(self, query_embedding: List[float], top_k: int = 10, filter_dict: dict = None) -> List[Dict[str, Any]]:
        """
        Search for top_k similar chunks.
        """
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=filter_dict
        )
        
        # Format results
        output = []
        if not results['ids'] or not results['ids'][0]:
            return output
            
        for i in range(len(results['ids'][0])):
            chunk_id = results['ids'][0][i]
            content = results['documents'][0][i]
            metadata = results['metadatas'][0][i]
            distance = results['distances'][0][i] if 'distances' in results and results['distances'] else 0.0
            
            # ChromaDB uses distance (smaller is better). We can convert to similarity score.
            similarity = 1.0 / (1.0 + distance)
            
            output.append({
                "chunk_id": chunk_id,
                "content": content,
                "metadata": metadata,
                "score": similarity
            })
            
        return output

    def delete_document(self, document_id: str):
        """
        Delete all chunks associated with a document_id.
        """
        self.collection.delete(where={"document_id": str(document_id)})

vector_store = VectorStore()
