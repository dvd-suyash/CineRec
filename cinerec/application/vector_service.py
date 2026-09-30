import uuid
from typing import List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pgvector.sqlalchemy import vector

from cinerec.infrastructure.db.models.movie import Movie
from cinerec.infrastructure.db.models.memory import MovieEmbedding
from cinerec.domain.embedding.provider import EmbeddingProvider

class VectorService:
    def __init__(self, session: AsyncSession, provider: EmbeddingProvider):
        self.session = session
        self.provider = provider
        
    async def embed_movie(self, movie: Movie) -> MovieEmbedding:
        # Create a semantic representation of the movie
        text_representation = f"Title: {movie.title}. Overview: {movie.overview or ''}"
        vector_data = await self.provider.generate_embedding(text_representation)
        
        # Check if embedding already exists
        stmt = select(MovieEmbedding).where(MovieEmbedding.movie_id == movie.id)
        result = await self.session.execute(stmt)
        embedding_record = result.scalars().first()
        
        if embedding_record:
            embedding_record.embedding = vector_data
            embedding_record.model_name = self.provider.model_name
            embedding_record.model_version = self.provider.model_version
        else:
            embedding_record = MovieEmbedding(
                movie_id=movie.id,
                embedding_type="document",
                model_name=self.provider.model_name,
                model_version=self.provider.model_version,
                embedding=vector_data
            )
            self.session.add(embedding_record)
            
        await self.session.commit()
        return embedding_record
        
    async def exact_search_movies(self, query: str, limit: int = 10) -> List[Tuple[Movie, float]]:
        """Exact KNN search using cosine distance (<=> operator in pgvector)."""
        query_vector = await self.provider.generate_embedding(query)
        
        stmt = (
            select(Movie, MovieEmbedding.embedding.cosine_distance(query_vector).label("distance"))
            .join(MovieEmbedding, MovieEmbedding.movie_id == Movie.id)
            .order_by("distance")
            .limit(limit)
        )
        
        result = await self.session.execute(stmt)
        return result.all()
