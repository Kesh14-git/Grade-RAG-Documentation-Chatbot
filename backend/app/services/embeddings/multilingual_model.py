import logging
import os

from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

class MultilingualModel:
    def __init__(self, model_name="BAAI/bge-m3"):
        self.model_name = model_name
        self._model = None
        
    def get_model(self):
        if self._model is None:
            logger.info(f"Loading multilingual model: {self.model_name}")
            try:
                import torch
                device = "mps" if torch.backends.mps.is_available() else ("cuda" if torch.cuda.is_available() else "cpu")
                logger.info(f"Using device: {device} for multilingual embedding")
                # bge-m3 can be quite large, we assume the environment has enough RAM.
                self._model = SentenceTransformer(self.model_name, device=device)
            except Exception as e:
                logger.error(f"Failed to load multilingual model {self.model_name}: {e}")
                raise e
        return self._model

    def encode(self, texts: list[str]) -> list[list[float]]:
        model = self.get_model()
        # BGE-M3 returns embeddings. We can convert them to lists of floats.
        embeddings = model.encode(texts, normalize_embeddings=True, show_progress_bar=False)
        return embeddings.tolist()

multilingual_model = MultilingualModel()
