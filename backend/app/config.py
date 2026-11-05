from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    LLM_PROVIDER: str = "gemini"
    
    GEMINI_API_KEY: Optional[str] = None
    GEMINI_MODEL: str = "gemini-2.5-flash"
    
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4o-mini"
    
    EMBEDDING_PROVIDER: str = "gemini"
    EMBEDDING_MODEL: str = "text-embedding-004"
    
    VECTOR_STORE_PATH: str = "./chroma_db"
    DENSE_WEIGHT: float = 0.7
    BM25_WEIGHT: float = 0.3
    
    TOP_K: int = 15
    RERANK_TOP_K: int = 5
    MAX_CONTEXT_TOKENS: int = 8000
    
    # Query Rewriting
    QUERY_REWRITING_ENABLED: bool = True
    QUERY_REWRITE_MAX_TURNS: int = 6
    
    # Guardrails
    GUARDRAILS_ENABLED: bool = True
    PROMPT_INJECTION_GUARD_ENABLED: bool = True
    CONTEXT_GUARD_ENABLED: bool = True
    GROUNDING_GUARD_ENABLED: bool = True
    CITATION_GUARD_ENABLED: bool = True
    GROUNDING_THRESHOLD: float = 0.70
    MAX_GUARDRAIL_RETRIES: int = 1
    
    # Fastapi
    PROJECT_NAME: str = "Documentation Q&A RAG API"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
