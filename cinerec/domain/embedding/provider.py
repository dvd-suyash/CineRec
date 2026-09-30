from typing import Protocol, List

class EmbeddingProvider(Protocol):
    """
    Abstract interface for generating embeddings.
    Allows swapping text-embedding-models (e.g. Gemini, OpenAI, open-source).
    """
    
    @property
    def model_name(self) -> str:
        ...
        
    @property
    def model_version(self) -> str:
        ...
        
    @property
    def dimensions(self) -> int:
        ...

    async def generate_embedding(self, text: str) -> List[float]:
        """Generate a single embedding for the given text."""
        ...
        
    async def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts in batch."""
        ...
