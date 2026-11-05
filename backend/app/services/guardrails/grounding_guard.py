import logging
import json
from typing import List, Dict, Any
from app.services.llm.factory import llm_factory
from app.services.guardrails.models import GroundingResult
from app.config import settings

logger = logging.getLogger(__name__)

class GroundingGuard:
    def __init__(self):
        self.system_prompt = """You are an objective Grounding Evaluator.
Your task is to determine if a generated answer is fully supported by the provided retrieved context.
If the answer contains claims, numbers, or facts that conflict with or are absent from the context, it is NOT grounded.
If the context is insufficient, and the answer states that it cannot find the information, that IS grounded.

Return a JSON object matching this schema:
{
  "grounded": boolean,
  "score": float (0.0 to 1.0 confidence),
  "reason": string (brief explanation of why it is or isn't grounded)
}
"""

    def evaluate(self, answer: str, retrieved_chunks: List[Dict[str, Any]], user_query: str) -> GroundingResult:
        if not answer or not retrieved_chunks:
            # If there's no answer or no chunks, it defaults to grounded if the answer is the fallback rejection, else ungrounded
            is_fallback = "couldn't find" in answer.lower() or "error" in answer.lower()
            return GroundingResult(
                grounded=is_fallback, 
                score=1.0 if is_fallback else 0.0, 
                reason="Fallback behavior due to empty context or answer."
            )
            
        try:
            # Build context representation
            context_text = "\n\n".join([c.get('content', '') for c in retrieved_chunks])
            user_prompt = f"USER QUERY:\n{user_query}\n\nCONTEXT:\n{context_text}\n\nGENERATED ANSWER:\n{answer}\n\nEvaluate the grounding of the answer against the context."
            
            provider = llm_factory.get_llm_provider()
            
            # Using the main LLM provider to evaluate grounding.
            raw_response = provider.generate_response(
                system_prompt=self.system_prompt,
                user_prompt=user_prompt,
                response_schema=GroundingResult
            )
            
            cleaned = raw_response.strip()
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            elif cleaned.startswith("```"):
                cleaned = cleaned[3:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
                
            data = json.loads(cleaned.strip())
            
            result = GroundingResult(
                grounded=data.get('grounded', False),
                score=float(data.get('score', 0.0)),
                reason=data.get('reason', 'Failed to parse reasoning.')
            )
            
            if result.score < settings.GROUNDING_THRESHOLD:
                result.grounded = False
                result.reason += f" (Score {result.score} is below threshold {settings.GROUNDING_THRESHOLD})"
                
            return result
            
        except Exception as e:
            logger.error(f"GroundingGuard evaluation failed: {e}")
            # Fail safe: if the evaluator crashes, we don't crash the pipeline, we just mark it as unverified
            return GroundingResult(
                grounded=True, 
                score=0.0, 
                reason="Grounding evaluation failed due to internal error. Answer passed through safely."
            )

grounding_guard = GroundingGuard()
