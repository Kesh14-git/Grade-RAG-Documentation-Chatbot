import re
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class ContextGuard:
    def __init__(self):
        # We share patterns with InputGuard but apply them to document context.
        self.injection_patterns = [
            r"(ignore\s+(all\s+)?previous\s+instructions)",
            r"(ignore\s+(the\s+)?system\s+prompt)",
            r"(reveal\s+(your\s+)?system\s+prompt)",
            r"(disregard\s+(all\s+)?previous\s+instructions)",
            r"(you\s+are\s+now\s+an\s+unrestricted\s+assistant)",
            r"(new\s+rule(s)?):",
            r"(system\s+override)"
        ]
        self.compiled_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in self.injection_patterns]

    def sanitize_context(self, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Scans retrieved chunks for malicious instruction overrides.
        If found, replaces the malicious string with a safe placeholder to preserve surrounding data.
        """
        sanitized_chunks = []
        for chunk in chunks:
            original_content = chunk.get('content', '')
            sanitized_content = original_content
            was_modified = False
            
            for pattern in self.compiled_patterns:
                if pattern.search(sanitized_content):
                    was_modified = True
                    logger.warning(f"ContextGuard: Suspicious instruction found in chunk from {chunk['metadata'].get('document_name', 'Unknown')}. Redacting.")
                    sanitized_content = pattern.sub("[REDACTED POTENTIAL INJECTION]", sanitized_content)
            
            # Create a shallow copy to avoid mutating the original retrieved object if it's cached elsewhere
            new_chunk = chunk.copy()
            if was_modified:
                new_chunk['content'] = f"[WARNING: UNTRUSTED CONTENT DETECTED] {sanitized_content}"
            else:
                new_chunk['content'] = sanitized_content
                
            sanitized_chunks.append(new_chunk)
            
        return sanitized_chunks

context_guard = ContextGuard()
