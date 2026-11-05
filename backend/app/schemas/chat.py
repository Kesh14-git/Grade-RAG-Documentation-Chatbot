from pydantic import BaseModel
from typing import List, Optional, Any

class Message(BaseModel):
    role: str
    content: str

class StructuredResource(BaseModel):
    document_name: str
    page_number: str
    exact_quote: str

class StructuredAnswer(BaseModel):
    result: str
    resources: List[StructuredResource]

class ChatRequest(BaseModel):
    query: str
    history: Optional[List[Message]] = None
    document_ids: Optional[List[str]] = None
    response_language: Optional[str] = "Auto"

class Citation(BaseModel):
    document_name: str
    page_number: Any
    content: str
    score: float
    base64_image: Optional[str] = None

class GuardrailMetadata(BaseModel):
    prompt_injection_detected: bool = False
    grounded: bool = True
    grounding_score: Optional[float] = None
    citations_valid: bool = True
    reason: Optional[str] = None

class ChatResponse(BaseModel):
    answer: str
    citations: List[Citation]
    normalized_query: Optional[str] = None
    rewritten_query: Optional[str] = None
    query_analysis: Optional[Any] = None
    resources: Optional[List[StructuredResource]] = None
    guardrails: Optional[GuardrailMetadata] = None
