import logging
from typing import List, Dict, Any, Tuple
from app.schemas.chat import GuardrailMetadata, StructuredResource
from app.services.guardrails.input_guard import input_guard
from app.services.guardrails.context_guard import context_guard
from app.services.guardrails.citation_guard import citation_guard
from app.services.guardrails.grounding_guard import grounding_guard
from app.config import settings

logger = logging.getLogger(__name__)

class GuardrailService:
    def check_input(self, query: str) -> Tuple[bool, str]:
        """
        Returns (is_safe, rejection_message)
        """
        if not settings.GUARDRAILS_ENABLED or not settings.PROMPT_INJECTION_GUARD_ENABLED:
            return True, ""
            
        if not input_guard.check_input(query):
            return False, "I cannot process this request because it violates safety policies regarding system instructions."
            
        return True, ""

    def sanitize_context(self, retrieved_chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        if not settings.GUARDRAILS_ENABLED or not settings.CONTEXT_GUARD_ENABLED:
            return retrieved_chunks
            
        return context_guard.sanitize_context(retrieved_chunks)

    def evaluate_output(self, answer: str, generated_resources: List[StructuredResource], retrieved_chunks: List[Dict[str, Any]], user_query: str) -> GuardrailMetadata:
        metadata = GuardrailMetadata()
        
        if not settings.GUARDRAILS_ENABLED:
            return metadata

        # 1. Validate Citations
        if settings.CITATION_GUARD_ENABLED:
            citation_res = citation_guard.validate_citations(generated_resources, retrieved_chunks)
            metadata.citations_valid = citation_res.valid
            if not citation_res.valid:
                metadata.reason = citation_res.reason
                
        # 2. Validate Grounding (Only if citations are valid or if we want to check anyway)
        if settings.GROUNDING_GUARD_ENABLED:
            grounding_res = grounding_guard.evaluate(answer, retrieved_chunks, user_query)
            metadata.grounded = grounding_res.grounded
            metadata.grounding_score = grounding_res.score
            if not grounding_res.grounded:
                # Prioritize grounding reason if it failed
                metadata.reason = grounding_res.reason

        return metadata

guardrail_service = GuardrailService()
