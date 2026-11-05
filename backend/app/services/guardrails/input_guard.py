import re
import logging

logger = logging.getLogger(__name__)

class InputGuard:
    def __init__(self):
        # A lightweight set of deterministic patterns to detect prompt injection
        self.injection_patterns = [
            r"ignore\s+(all\s+)?previous\s+instructions",
            r"ignore\s+(the\s+)?system\s+prompt",
            r"reveal\s+(your\s+)?system\s+prompt",
            r"disregard\s+(all\s+)?previous\s+instructions",
            r"you\s+are\s+now\s+an\s+unrestricted\s+assistant",
            r"new\s+rule(s)?:",
            r"system\s+override",
            r"make\s+this\s+as\s+(a\s+)?pirate",
            r"act\s+as\s+(a\s+)?pirate",
            r"act\s+like\s+a",
            r"pretend\s+to\s+be",
            r"pass\s+the\s+instructions"
        ]
        self.compiled_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in self.injection_patterns]

    def check_input(self, query: str) -> bool:
        """
        Returns True if the input is SAFE.
        Returns False if the input is MALICIOUS.
        """
        for pattern in self.compiled_patterns:
            if pattern.search(query):
                logger.warning(f"InputGuard: Malicious input detected. Matched pattern: {pattern.pattern}")
                return False
        return True

input_guard = InputGuard()
