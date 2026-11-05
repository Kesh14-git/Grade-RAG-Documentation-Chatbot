from app.config import settings
from app.services.llm.base import LLMProvider, EmbeddingProvider
from app.services.llm.gemini_provider import GeminiLLMProvider, GeminiEmbeddingProvider
from app.services.llm.openai_provider import OpenAILLMProvider, OpenAIEmbeddingProvider
from app.services.llm.mock_provider import MockLLMProvider, MockEmbeddingProvider
import logging

logger = logging.getLogger(__name__)

class LLMFactory:
    @staticmethod
    def _is_valid_key(key):
        return key and key not in ["your_gemini_api_key_here", "your_openai_api_key_here"]

    @staticmethod
    def get_llm_provider() -> LLMProvider:
        if settings.LLM_PROVIDER.lower() == "gemini":
            if LLMFactory._is_valid_key(settings.GEMINI_API_KEY):
                return GeminiLLMProvider()
            logger.warning("No valid Gemini API key. Using Mock LLM.")
            return MockLLMProvider()
        elif settings.LLM_PROVIDER.lower() == "openai":
            if LLMFactory._is_valid_key(settings.OPENAI_API_KEY):
                return OpenAILLMProvider()
            logger.warning("No valid OpenAI API key. Using Mock LLM.")
            return MockLLMProvider()
        return MockLLMProvider()

    @staticmethod
    def get_embedding_provider() -> EmbeddingProvider:
        if settings.EMBEDDING_PROVIDER.lower() == "gemini":
            if LLMFactory._is_valid_key(settings.GEMINI_API_KEY):
                return GeminiEmbeddingProvider()
            logger.warning("No valid Gemini API key. Using Mock Embedding.")
            return MockEmbeddingProvider()
        elif settings.EMBEDDING_PROVIDER.lower() == "openai":
            if LLMFactory._is_valid_key(settings.OPENAI_API_KEY):
                return OpenAIEmbeddingProvider()
            logger.warning("No valid OpenAI API key. Using Mock Embedding.")
            return MockEmbeddingProvider()
        return MockEmbeddingProvider()

llm_factory = LLMFactory()
