from typing import List, Dict, Optional
from app.services.llm.factory import llm_factory
from app.config import settings
from app.services.query_rewriting.prompts import QUERY_REWRITE_SYSTEM_PROMPT
from app.services.query_rewriting.detector import detector
import logging

logger = logging.getLogger(__name__)

class QueryRewriter:
    def __init__(self):
        self.llm_provider = llm_factory.get_llm_provider()
        self.system_prompt = QUERY_REWRITE_SYSTEM_PROMPT

    def rewrite(self, query: str, history: Optional[List[Dict[str, str]]] = None) -> str:
        # Fallback 1: Feature disabled
        if not getattr(settings, "QUERY_REWRITING_ENABLED", True):
            logger.info("Query rewriting disabled in config.")
            return query
            
        # Fallback 2: No history
        if not history or len(history) == 0:
            logger.info("No history provided. Skipping query rewriting.")
            return query
            
        # Context Dependency Detection
        status = detector.analyze(query)
        if status == "SELF_CONTAINED":
            logger.info(f"Query detected as {status}. Skipping rewrite.")
            return query
            
        try:
            # We don't send the entire history. Use setting or default to 6
            max_turns = getattr(settings, "QUERY_REWRITE_MAX_TURNS", 6)
            history_text = "\n".join([f"{msg['role'].capitalize()}: {msg['content']}" for msg in history[-max_turns:]])
            
            user_prompt = f"CONVERSATION HISTORY:\n{history_text}\n\nNEW QUERY:\n{query}\n\nREWRITTEN QUERY:"
            
            rewritten = self.llm_provider.generate_response(
                system_prompt=self.system_prompt,
                user_prompt=user_prompt
            )
            
            rewritten = rewritten.strip(' "\'\n')
            
            # Fallback 3: Empty response
            if not rewritten:
                logger.warning("Rewrite returned empty string. Fallback used: true")
                return query
                
            logger.info("Rewrite performed: true")
            logger.info(f"Original query: {query}")
            logger.info(f"Rewritten query: {rewritten}")
            return rewritten
            
        except Exception as e:
            # Fallback 4: Any exception
            logger.error(f"Error during query rewriting: {e}. Fallback used: true")
            return query

query_rewriter = QueryRewriter()
