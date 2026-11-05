import os
import sys
from dotenv import load_dotenv
load_dotenv()

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))

from app.services.retrieval.hybrid_retriever import hybrid_retriever
from app.services.query_normalization.normalizer import query_normalizer

def compare_retrieval(noisy_query: str):
    print(f"\n{'='*50}")
    print(f"EVALUATING RETRIEVAL IMPACT")
    print(f"{'='*50}")
    
    print(f"RAW QUERY: '{noisy_query}'")
    
    normalized = query_normalizer.normalize(noisy_query)["normalized_query"]
    print(f"NORMALIZED QUERY: '{normalized}'\n")

    # Before
    try:
        results_before = hybrid_retriever.retrieve(noisy_query, None)
        scores_before = [res.get('fused_score', res.get('rerank_score', 0)) for res in results_before]
    except Exception as e:
        print(f"Before retrieval failed: {e}")
        scores_before = []

    # After
    try:
        results_after = hybrid_retriever.retrieve(normalized, None)
        scores_after = [res.get('fused_score', res.get('rerank_score', 0)) for res in results_after]
    except Exception as e:
        print(f"After retrieval failed: {e}")
        scores_after = []
        
    print("--- BEFORE NORMALIZATION ---")
    print(f"Top-K Chunks Retrieved: {len(scores_before)}")
    print(f"Scores: {scores_before}")
    
    print("\n--- AFTER NORMALIZATION ---")
    print(f"Top-K Chunks Retrieved: {len(scores_after)}")
    print(f"Scores: {scores_after}")
    
    # Simple heuristic comparison
    if len(scores_after) == 0 and len(scores_before) == 0:
        print("\nCONCLUSION: NO DOCUMENTS FOUND FOR BOTH.")
    elif len(scores_after) > len(scores_before):
        print("\nCONCLUSION: NORMALIZATION IMPROVED RECALL (More chunks found).")
    elif len(scores_after) == len(scores_before) and sum(scores_after) > sum(scores_before):
        print("\nCONCLUSION: NORMALIZATION IMPROVED RELEVANCE SCORES.")
    elif len(scores_after) == len(scores_before) and sum(scores_after) == sum(scores_before):
        print("\nCONCLUSION: NEUTRAL (Retriever handled raw query equally well).")
    else:
        print("\nCONCLUSION: NORMALIZATION DEGRADED RESULTS.")

if __name__ == "__main__":
    # Test an extremely noisy query where whitespace and typos matter for BM25
    compare_retrieval("   what   is   novatech's   revnue in 2025???? ")
