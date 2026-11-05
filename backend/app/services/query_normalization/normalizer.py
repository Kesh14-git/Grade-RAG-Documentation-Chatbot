import re
import unicodedata
from typing import Dict, Any, List

class QueryNormalizer:
    def __init__(self):
        # Known domain terminology mapping (lowercase key -> correct case/spelling)
        self.domain_dictionary = {
            "novatech": "NovaTech",
            "api": "API",
            "gpt-4": "GPT-4",
            "rinvoq": "Rinvoq",
            "revnue": "revenue",
            "rev": "revenue", # Confident expansion based on domain
            "what's": "what is",
            "whats": "what is"
        }
        
        # We only want to expand 'rev' if it's a whole word, not part of 'revenue'
        self.word_replacements = {
            r'\bwhats\b': 'what is',
            r'\bwhat\'s\b': 'what is',
            r'\brevnue\b': 'revenue',
            r'\brev\b': 'revenue'
        }

    def normalize(self, query: str) -> Dict[str, Any]:
        original_query = query
        changes_applied = []
        
        if not query or not query.strip():
            return {
                "original_query": original_query,
                "normalized_query": query,
                "normalization_applied": False,
                "changes": changes_applied
            }

        # 1. Unicode Normalization (NFKC standardizes visually equivalent characters)
        norm_query = unicodedata.normalize('NFKC', query)
        if norm_query != query:
            changes_applied.append("unicode_normalized")
            
        # 2. Smart Quotes & Apostrophes
        quote_map = {
            '‘': "'", '’': "'", '“': '"', '”': '"', '´': "'"
        }
        for smart, straight in quote_map.items():
            norm_query = norm_query.replace(smart, straight)
            
        # 3. Collapse excessive repeated punctuation
        # E.g. "revenue?????" -> "revenue?"
        norm_query_punct = re.sub(r'(\?){2,}', '?', norm_query)
        norm_query_punct = re.sub(r'(!){2,}', '!', norm_query_punct)
        if norm_query_punct != norm_query:
            changes_applied.append("punctuation_normalized")
        norm_query = norm_query_punct

        # 4. Whitespace Normalization
        norm_query_space = re.sub(r'\s+', ' ', norm_query).strip()
        if norm_query_space != norm_query:
            changes_applied.append("whitespace_normalized")
        norm_query = norm_query_space

        # 5. Case and Typo Normalization (Deterministic)
        # If the query is entirely UPPERCASE, we convert to lowercase so our dictionary can fix entities
        is_all_caps = norm_query.isupper()
        if is_all_caps:
            norm_query = norm_query.lower()
            changes_applied.append("all_caps_lowercased")

        # Apply whole-word replacements (case-insensitive where safe)
        for pattern, replacement in self.word_replacements.items():
            # Use regex to replace whole words, ignoring case
            new_query = re.sub(pattern, replacement, norm_query, flags=re.IGNORECASE)
            if new_query != norm_query:
                changes_applied.append(f"typo_corrected_{replacement.replace(' ', '_')}")
            norm_query = new_query

        # Domain entity case preservation
        # Tokenize by word boundaries, but keep the exact spacing/punctuation
        def replacer(match):
            word = match.group(0)
            word_lower = word.lower()
            if word_lower in self.domain_dictionary:
                return self.domain_dictionary[word_lower]
            return word

        norm_query_entities = re.sub(r'\b[\w-]+\b', replacer, norm_query)
        if norm_query_entities != norm_query:
            changes_applied.append("domain_entities_preserved")
        norm_query = norm_query_entities

        # If it was all caps, we might want to capitalize the first letter to make it a proper sentence again
        if is_all_caps and len(norm_query) > 0:
            norm_query = norm_query[0].upper() + norm_query[1:]

        # Clean up list uniqueness
        changes_applied = list(dict.fromkeys(changes_applied))

        return {
            "original_query": original_query,
            "normalized_query": norm_query,
            "normalization_applied": len(changes_applied) > 0,
            "changes": changes_applied
        }

query_normalizer = QueryNormalizer()
