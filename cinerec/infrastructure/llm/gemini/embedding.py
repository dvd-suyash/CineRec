from typing import List
from google import genai
from cinerec.domain.embedding.provider import EmbeddingProvider
from cinerec.core.config import settings

class GeminiEmbeddingProvider(EmbeddingProvider):
    def __init__(self):
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY.get_secret_value())
        self._model_name = "text-embedding-004"
        self._model_version = "v1"
        self._dimensions = 768

    @property
    def model_name(self) -> str:
        return self._model_name
        
    @property
    def model_version(self) -> str:
        return self._model_version
        
    @property
    def dimensions(self) -> int:
        return self._dimensions

    async def generate_embedding(self, text: str) -> List[float]:
        response = await self.client.aio.models.embed_content(
            model=self._model_name,
            contents=text
        )
        # Handle new SDK response shape properly
        return response.embeddings[0].values

    async def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        response = await self.client.aio.models.embed_content(
            model=self._model_name,
            contents=texts
        )
        return [e.values for e in response.embeddings]
