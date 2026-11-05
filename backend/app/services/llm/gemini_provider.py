from typing import List, Dict, Any, Optional
from google import genai
from google.genai import types
from app.config import settings
from app.services.llm.base import LLMProvider, EmbeddingProvider

class GeminiLLMProvider(LLMProvider):
    def __init__(self):
        if not settings.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is not set.")
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
        self.model_name = settings.GEMINI_MODEL

    def generate_response(self, system_prompt: str, user_prompt: str, history: Optional[List[Dict[str, str]]] = None, images: Optional[List[str]] = None, response_schema: Optional[Any] = None) -> str:
        import base64
        contents = []
        if history:
            for msg in history:
                role = 'user' if msg['role'] == 'user' else 'model'
                contents.append(types.Content(role=role, parts=[types.Part.from_text(text=msg['content'])]))
        
        user_parts = [types.Part.from_text(text=user_prompt)]
        if images:
            for img_b64 in images:
                try:
                    img_bytes = base64.b64decode(img_b64)
                    user_parts.append(types.Part.from_bytes(data=img_bytes, mime_type="image/png"))
                except Exception as e:
                    print(f"Failed to decode image: {e}")
        
        contents.append(types.Content(role='user', parts=user_parts))
        
        if response_schema:
            config = types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=0.0,
                response_mime_type="application/json",
                response_schema=response_schema
            )
        else:
            config = types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=0.0
            )
        
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=contents,
            config=config
        )
        return response.text

    def generate_response_stream(self, system_prompt: str, user_prompt: str, history: Optional[List[Dict[str, str]]] = None, images: Optional[List[str]] = None):
        import base64
        contents = []
        if history:
            for msg in history:
                role = 'user' if msg['role'] == 'user' else 'model'
                contents.append(types.Content(role=role, parts=[types.Part.from_text(text=msg['content'])]))
        
        user_parts = [types.Part.from_text(text=user_prompt)]
        if images:
            for img_b64 in images:
                try:
                    img_bytes = base64.b64decode(img_b64)
                    user_parts.append(types.Part.from_bytes(data=img_bytes, mime_type="image/png"))
                except Exception as e:
                    print(f"Failed to decode image: {e}")
        
        contents.append(types.Content(role='user', parts=user_parts))
        
        config = types.GenerateContentConfig(
            system_instruction=system_prompt,
            temperature=0.0
        )
        
        response = self.client.models.generate_content_stream(
            model=self.model_name,
            contents=contents,
            config=config
        )
        
        for chunk in response:
            if chunk.text:
                yield chunk.text

class GeminiEmbeddingProvider(EmbeddingProvider):
    def __init__(self):
        if not settings.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is not set.")
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
        self.model_name = settings.EMBEDDING_MODEL

    def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        all_embeddings = []
        batch_size = 100
        
        for i in range(0, len(texts), batch_size):
            batch_texts = texts[i:i + batch_size]
            try:
                response = self.client.models.embed_content(
                    model=self.model_name,
                    contents=batch_texts
                )
                all_embeddings.extend([embedding.values for embedding in response.embeddings])
            except Exception as e:
                if "404" in str(e) or "NOT_FOUND" in str(e):
                    print(f"Model {self.model_name} failed. Falling back to embedding-001")
                    try:
                        response = self.client.models.embed_content(
                            model="embedding-001",
                            contents=batch_texts
                        )
                        all_embeddings.extend([embedding.values for embedding in response.embeddings])
                    except Exception as e2:
                        print(f"embedding-001 also failed. Falling back to Mock embeddings.")
                        from app.services.llm.mock_provider import MockEmbeddingProvider
                        mock_provider = MockEmbeddingProvider()
                        all_embeddings.extend(mock_provider.get_embeddings(batch_texts))
                else:
                    raise e
        return all_embeddings
