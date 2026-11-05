import json
import logging
from typing import Dict, Any
from app.services.llm.factory import llm_factory

logger = logging.getLogger(__name__)

from pydantic import BaseModel, Field
from typing import List

class QueryAnalysisSchema(BaseModel):
    intent: str
    complexity: str
    confidence: float
    reason_codes: List[str]

class QueryAnalyzer:
    def __init__(self):
        self.llm_provider = llm_factory.get_llm_provider()
        self.system_prompt = """You are a Query Analysis engine for a RAG system.
Your task is to classify the intent and complexity of the user's search query. This query may be in any language.

Intents: factual, numerical, comparison, analytical, summary, definition, multi-hop, conversational, unknown.
Complexity: low, medium, high.

Rules:
- Reason codes must be short snake_case labels describing observable characteristics (e.g. "multiple_entities", "cross_document_comparison").
- Treat the query semantics independent of language. A comparison in Tamil is still a comparison intent."""

    def analyze(self, query: str) -> Dict[str, Any]:
        default_error = {
            "intent": "unknown",
            "complexity": "unknown",
            "confidence": 0.0,
            "reason_codes": ["analysis_failed"]
        }
        
        try:
            response = self.llm_provider.generate_response(
                system_prompt=self.system_prompt,
                user_prompt=query,
                response_schema=QueryAnalysisSchema
            )
            
            # Clean possible markdown wrapping
            cleaned = response.strip()
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            elif cleaned.startswith("```"):
                cleaned = cleaned[3:]
                
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
                
            cleaned = cleaned.strip()
            result = json.loads(cleaned)
            
            # Ensure required keys exist
            for key in ["intent", "complexity", "confidence", "reason_codes"]:
                if key not in result:
                    result[key] = default_error[key]
                    
            return result
        except Exception as e:
            logger.error(f"Query analysis failed for query '{query}': {e}")
            return default_error

query_analyzer = QueryAnalyzer()
