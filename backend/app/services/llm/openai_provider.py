from typing import List, Dict, Any, Optional
from openai import OpenAI
from app.config import settings
from app.services.llm.base import LLMProvider, EmbeddingProvider

class OpenAILLMProvider(LLMProvider):
    def __init__(self):
        if not settings.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is not set.")
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model_name = settings.OPENAI_MODEL

    def generate_response(self, system_prompt: str, user_prompt: str, history: Optional[List[Dict[str, str]]] = None, images: Optional[List[str]] = None) -> str:
        messages = [{"role": "system", "content": system_prompt}]
        
        if history:
            for msg in history:
                messages.append({"role": msg["role"], "content": msg["content"]})
                
        user_content = [{"type": "text", "text": user_prompt}]
        if images:
            for img_b64 in images:
                user_content.append({"type": "image_url", "image_url": {"url": f"data:image/png;base64,{img_b64}"}})
                
        messages.append({"role": "user", "content": user_content})
        
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            temperature=0.0
        )
        return response.choices[0].message.content

    def generate_response_stream(self, system_prompt: str, user_prompt: str, history: Optional[List[Dict[str, str]]] = None, images: Optional[List[str]] = None):
        messages = [{"role": "system", "content": system_prompt}]
        
        if history:
            for msg in history:
                messages.append({"role": msg["role"], "content": msg["content"]})
                
        user_content = [{"type": "text", "text": user_prompt}]
        if images:
            for img_b64 in images:
                user_content.append({"type": "image_url", "image_url": {"url": f"data:image/png;base64,{img_b64}"}})
                
        messages.append({"role": "user", "content": user_content})
        
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            temperature=0.0,
            stream=True
        )
        
        for chunk in response:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

class OpenAIEmbeddingProvider(EmbeddingProvider):
    def __init__(self):
        if not settings.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is not set.")
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model_name = settings.EMBEDDING_MODEL

    def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        response = self.client.embeddings.create(
            input=texts,
            model=self.model_name
        )
        return [data.embedding for data in response.data]
