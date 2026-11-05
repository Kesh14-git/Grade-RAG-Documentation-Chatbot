import math
from typing import List, Dict, Any
from app.config import settings
from app.services.retrieval.vector_store import vector_store
from app.services.retrieval.bm25_store import bm25_store
from app.services.llm.factory import llm_factory
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Try to import CrossEncoder, handle fallback if not available
try:
    import torch
    device = "mps" if torch.backends.mps.is_available() else ("cuda" if torch.cuda.is_available() else "cpu")
    logger.info(f"Using device: {device} for CrossEncoder")
    from sentence_transformers import CrossEncoder
    # Using a fast, lightweight reranker
    reranker_model = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2", device=device)
    RERANKER_AVAILABLE = True
except Exception as e:
    logger.warning(f"Could not load CrossEncoder: {e}. Falling back to hybrid fusion only.")
    RERANKER_AVAILABLE = False


class HybridRetriever:
    def __init__(self):
        self.embedding_provider = llm_factory.get_embedding_provider()

    def _normalize_scores(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        if not results:
            return []
        
        scores = [r["score"] for r in results]
        min_score = min(scores)
        max_score = max(scores)
        
        for r in results:
            if max_score > min_score:
                r["normalized_score"] = (r["score"] - min_score) / (max_score - min_score)
            else:
                r["normalized_score"] = 1.0
        return results

    def retrieve(self, query: str, top_k: int = None, filter_dict: dict = None) -> List[Dict[str, Any]]:
        top_k = top_k or settings.TOP_K
        
        # 1. Detect query language
        try:
            from app.services.utils.language_detector import language_detector
            query_lang = language_detector.detect_language(query)
            logger.info(f"Detected query language: {query_lang}")
        except Exception:
            query_lang = 'en'
            
        # 2. Dense Retrieval (Language Routed)
        dense_results = []
        if query_lang == 'en':
            try:
                query_embedding = self.embedding_provider.get_embeddings([query])[0]
                if query_embedding:
                    dense_results = vector_store.search(query_embedding, top_k=top_k, filter_dict=filter_dict)
            except Exception as e:
                logger.error(f"Failed to generate English query embedding: {e}")
        else:
            try:
                from app.services.embeddings.multilingual_model import multilingual_model
                from app.services.retrieval.multilingual_vector_store import multilingual_vector_store
                logger.info("Using multilingual dense retrieval")
                query_embedding = multilingual_model.encode([query])[0]
                if query_embedding:
                    dense_results = multilingual_vector_store.search(query_embedding, top_k=top_k, filter_dict=filter_dict)
            except Exception as e:
                logger.error(f"Failed to generate multilingual query embedding: {e}")
                
        dense_results = self._normalize_scores(dense_results)

        # 3. Retrieve from BM25 Store
        sparse_results = bm25_store.search(query, top_k=top_k, filter_dict=filter_dict)
        sparse_results = self._normalize_scores(sparse_results)

        # 4. Fusion
        fused_scores = {}
        chunks_map = {}
        
        # We need to map chunk_id to its full data
        for r in dense_results:
            cid = r["chunk_id"]
            chunks_map[cid] = r
            fused_scores[cid] = r["normalized_score"] * settings.DENSE_WEIGHT
            
        for r in sparse_results:
            cid = r["chunk_id"]
            if cid not in chunks_map:
                chunks_map[cid] = r
                fused_scores[cid] = r["normalized_score"] * settings.BM25_WEIGHT
            else:
                fused_scores[cid] += r["normalized_score"] * settings.BM25_WEIGHT

        # Sort by fused score
        fused_results = []
        for cid, score in sorted(fused_scores.items(), key=lambda x: x[1], reverse=True):
            chunk = chunks_map[cid]
            chunk["fused_score"] = score
            fused_results.append(chunk)

        # 5. Reranking (optional but recommended)
        rerank_top_k = settings.RERANK_TOP_K
        candidates = fused_results[:top_k] # We rerank the top candidates
        
        if RERANKER_AVAILABLE and candidates:
            try:
                pairs = [[query, doc["content"]] for doc in candidates]
                cross_scores = reranker_model.predict(pairs)
                
                for i, score in enumerate(cross_scores):
                    candidates[i]["rerank_score"] = float(score)
                    
                # Resort by rerank score
                candidates.sort(key=lambda x: x["rerank_score"], reverse=True)
            except Exception as e:
                logger.error(f"Reranking failed: {e}")
                
        return candidates[:rerank_top_k]

hybrid_retriever = HybridRetriever()
