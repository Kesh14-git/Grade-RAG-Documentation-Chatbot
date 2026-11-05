from typing import List, Dict, Any, Optional
from app.services.llm.base import LLMProvider, EmbeddingProvider
import random

class MockLLMProvider(LLMProvider):
    def generate_response(self, system_prompt: str, user_prompt: str, history: Optional[List[Dict[str, str]]] = None, images: Optional[List[str]] = None) -> str:
        return f"[MOCK MODE] Based on the context, I am answering your question: '{user_prompt}'. This is a simulated response because no valid API key was provided."

    def generate_response_stream(self, system_prompt: str, user_prompt: str, history: Optional[List[Dict[str, str]]] = None, images: Optional[List[str]] = None):
        import time
        response = f"[MOCK MODE] Based on the context, I am answering your question: '{user_prompt}'. This is a simulated streamed response."
        words = response.split(" ")
        for word in words:
            time.sleep(0.05)
            yield word + " "

class MockEmbeddingProvider(EmbeddingProvider):
    def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        # Return random 768-dimensional embeddings
        return [[random.uniform(-1.0, 1.0) for _ in range(768)] for _ in texts]
