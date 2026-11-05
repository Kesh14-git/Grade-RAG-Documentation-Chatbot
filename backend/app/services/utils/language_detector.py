from langdetect import detect, detect_langs, DetectorFactory
import logging

logger = logging.getLogger(__name__)

# Set seed for deterministic detection
DetectorFactory.seed = 0

class LanguageDetector:
    def __init__(self):
        pass

    def detect_language(self, text: str) -> str:
        """
        Returns the ISO 639-1 language code of the text.
        Defaults to 'en' on failure.
        """
        try:
            # We require at least some non-trivial text
            if not text or len(text.strip()) < 2:
                return 'en'
                
            lang = detect(text)
            return lang
        except Exception as e:
            logger.warning(f"Language detection failed for '{text}': {e}. Defaulting to 'en'.")
            return 'en'
            
    def is_english(self, text: str) -> bool:
        return self.detect_language(text) == 'en'

language_detector = LanguageDetector()
