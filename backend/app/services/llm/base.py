from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

class LLMProvider(ABC):
    @abstractmethod
    def generate_response(self, system_prompt: str, user_prompt: str, history: Optional[List[Dict[str, str]]] = None, images: Optional[List[str]] = None, response_schema: Optional[Any] = None) -> str:
        """
        Generates a response from the LLM.
        history is a list of dictionaries with 'role' and 'content'.
        response_schema can be a Pydantic BaseModel for structured outputs.
        """
        pass

    @abstractmethod
    def generate_response_stream(self, system_prompt: str, user_prompt: str, history: Optional[List[Dict[str, str]]] = None, images: Optional[List[str]] = None):
        """
        Yields chunks of the response from the LLM.
        """
        pass

class EmbeddingProvider(ABC):
    @abstractmethod
    def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Returns embeddings for a list of texts.
        """
        pass
