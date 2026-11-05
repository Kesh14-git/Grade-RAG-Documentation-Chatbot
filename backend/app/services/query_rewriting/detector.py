from typing import List, Dict, Optional
import re

class ConversationDetector:
    """
    Lightweight context-dependency detector.
    Determines if a query is SELF_CONTAINED or CONTEXT_DEPENDENT based on simple heuristics.
    """
    def __init__(self):
        # Pronouns, continuation words, and ambiguous references
        self.context_dependent_words = {
            "it", "its", "they", "them", "their", "this", "that", "those",
            "he", "she", "him", "her", "his", "these"
        }
        
        # Phrases that almost always require context
        self.context_phrases = [
            r"\bwhat about\b",
            r"\bhow about\b",
            r"\bcan you elaborate\b",
            r"\bmore details\b",
            r"\btell me more\b",
            r"^why\?*$",
            r"^how\?*$",
            r"^when\?*$"
        ]

    def analyze(self, query: str) -> str:
        """Returns 'CONTEXT_DEPENDENT' or 'SELF_CONTAINED'"""
        query_lower = query.lower()
        
        # Check explicit phrases
        for phrase in self.context_phrases:
            if re.search(phrase, query_lower):
                return "CONTEXT_DEPENDENT"
                
        # Check specific standalone words
        words = set(re.findall(r'\b\w+\b', query_lower))
        if bool(words.intersection(self.context_dependent_words)):
            return "CONTEXT_DEPENDENT"
            
        # Check if query is extremely short (e.g., just a year or a single word)
        if len(words) <= 2:
            return "CONTEXT_DEPENDENT"
            
        return "SELF_CONTAINED"

detector = ConversationDetector()
