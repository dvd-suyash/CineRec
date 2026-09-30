from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from apps.api.app.dependencies.db import get_db_session
from cinerec.application.vector_service import VectorService
from cinerec.infrastructure.llm.gemini.embedding import GeminiEmbeddingProvider
from cinerec.application.schemas.movie import MovieSchema
from cinerec.core.api import DataResponse

router = APIRouter()

@router.get("/semantic", response_model=DataResponse[List[MovieSchema]])
async def semantic_search(
    q: str = Query(..., min_length=1),
    limit: int = 10,
    db: AsyncSession = Depends(get_db_session)
):
    provider = GeminiEmbeddingProvider()
    service = VectorService(db, provider)
    
    # Returns List[Tuple[Movie, distance]]
    results = await service.exact_search_movies(q, limit=limit)
    
    # Map to schema
    movies = [MovieSchema.model_validate(movie) for movie, distance in results]
    
    return DataResponse(data=movies)
