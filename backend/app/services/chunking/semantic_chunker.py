import re
import math
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

def cosine_similarity(v1: List[float], v2: List[float]) -> float:
    dot_product = sum(a * b for a, b in zip(v1, v2))
    norm_a = math.sqrt(sum(a * a for a in v1))
    norm_b = math.sqrt(sum(b * b for b in v2))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot_product / (norm_a * norm_b)

class SemanticChunker:
    def __init__(self, max_chunk_size: int = 1500, similarity_threshold: float = 0.3):
        self.max_chunk_size = max_chunk_size
        self.similarity_threshold = similarity_threshold

    def chunk_documents(self, blocks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Takes blocks from the PDFProcessor, perfectly splits them into sentences,
        and uses Hugging Face embeddings to group semantically similar sentences.
        """
        if not blocks:
            return []
            
        try:
            # We import locally to avoid circular import loops at startup
            from app.services.embeddings.multilingual_model import multilingual_model
        except Exception as e:
            logger.error(f"Failed to import multilingual model for chunking: {e}")
            return []

        # 1. Flatten blocks into a list of sentences with metadata
        sentences_metadata = []
        
        for block in blocks:
            text = block["content"]
            
            # If it's an image block description, treat it as its own isolated semantic unit
            if block.get("source_type") == "pdf_image":
                sentences_metadata.append({
                    "text": text,
                    "page": block["page_number"],
                    "doc_id": block["document_id"],
                    "doc_name": block["document_name"],
                    "img_b64": block.get("base64_image")
                })
                continue
                
            # Split text perfectly into sentences using regex (lookbehind for punctuation)
            # This prevents words from being brutally sliced.
            raw_sentences = re.split(r'(?<=[.!?])\s+', text)
            
            for sent in raw_sentences:
                sent = sent.strip()
                if len(sent) > 2:
                    sentences_metadata.append({
                        "text": sent,
                        "page": block["page_number"],
                        "doc_id": block["document_id"],
                        "doc_name": block["document_name"],
                        "img_b64": None
                    })
                    
        if not sentences_metadata:
            return []

        # 2. Generate embeddings for all sentences to measure topic similarity
        texts = [s["text"] for s in sentences_metadata]
        logger.info(f"Generating embeddings for {len(texts)} sentences for semantic chunking...")
        embeddings = multilingual_model.encode(texts)

        # 3. Group sentences based on Cosine Similarity
        chunks = []
        current_chunk_sentences = [sentences_metadata[0]["text"]]
        current_chunk_pages = {sentences_metadata[0]["page"]}
        current_chunk_images = [sentences_metadata[0]["img_b64"]] if sentences_metadata[0]["img_b64"] else []
        current_doc_id = sentences_metadata[0]["doc_id"]
        current_doc_name = sentences_metadata[0]["doc_name"]
        
        for i in range(1, len(sentences_metadata)):
            prev_emb = embeddings[i-1]
            curr_emb = embeddings[i]
            sim = cosine_similarity(prev_emb, curr_emb)
            
            sent_meta = sentences_metadata[i]
            sent_text = sent_meta["text"]
            
            current_text_length = sum(len(s) for s in current_chunk_sentences)
            
            # If similarity is high AND we haven't exceeded max chunk size, append to current chunk
            if sim >= self.similarity_threshold and (current_text_length + len(sent_text) < self.max_chunk_size):
                current_chunk_sentences.append(sent_text)
                current_chunk_pages.add(sent_meta["page"])
                if sent_meta["img_b64"]:
                    current_chunk_images.append(sent_meta["img_b64"])
            else:
                # Finalize current chunk
                chunk_data = {
                    "document_id": current_doc_id,
                    "document_name": current_doc_name,
                    "page_number": min(current_chunk_pages),
                    "content": " ".join(current_chunk_sentences),
                    "chunk_id": f"{current_doc_id}_chunk_{len(chunks)}"
                }
                if current_chunk_images:
                    chunk_data["base64_images"] = current_chunk_images.copy()
                chunks.append(chunk_data)
                
                # Start new chunk
                current_chunk_sentences = [sent_text]
                current_chunk_pages = {sent_meta["page"]}
                current_chunk_images = [sent_meta["img_b64"]] if sent_meta["img_b64"] else []
                current_doc_id = sent_meta["doc_id"]
                current_doc_name = sent_meta["doc_name"]
                
        # Append final chunk
        if current_chunk_sentences:
            chunk_data = {
                "document_id": current_doc_id,
                "document_name": current_doc_name,
                "page_number": min(current_chunk_pages),
                "content": " ".join(current_chunk_sentences),
                "chunk_id": f"{current_doc_id}_chunk_{len(chunks)}"
            }
            if current_chunk_images:
                chunk_data["base64_images"] = current_chunk_images.copy()
            chunks.append(chunk_data)
            
        logger.info(f"Semantically chunked into {len(chunks)} cohesive blocks.")
        return chunks

chunker = SemanticChunker()
