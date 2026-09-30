from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
import uuid
from typing import List

from apps.api.app.dependencies.db import get_db_session
from apps.api.app.dependencies.auth import get_current_user
from cinerec.infrastructure.db.models.user import User
from cinerec.core.api import DataResponse, MetaInfo
from cinerec.application.movie_service import MovieService
from cinerec.application.schemas.movie import MovieSchema
from cinerec.infrastructure.tmdb.adapter import TMDBAdapter

router = APIRouter()

@router.get("/search", response_model=DataResponse[List[MovieSchema]])
async def search_movies(
    q: str = Query(..., min_length=1),
    page: int = Query(1, ge=1),
    db: AsyncSession = Depends(get_db_session),
    # current_user: User = Depends(get_current_user) # Can be open or authenticated
):
    """Search for movies using the TMDB provider integration."""
    provider = TMDBAdapter()
    results = await provider.search_movies(query=q, page=page)
    
    # Normally we would normalize these search results to MovieSchema objects on the fly
    # For now, returning minimal representation directly (we should parse TMDB raw response)
    # The TMDBAdapter returns raw TMDB search payload. We should map it.
    
    # We will let the frontend use /movies/{provider_id} to fetch full detail.
    # In a full implementation we'd normalize here.
    mapped_movies = []
    for raw in results.get("results", []):
        mapped_movies.append(MovieSchema(
            id=uuid.uuid4(), # ephemeral for search list if not in DB
            title=raw.get("title", "Unknown"),
            overview=raw.get("overview"),
            poster_path=raw.get("poster_path"),
            release_year=int(raw["release_date"].split("-")[0]) if raw.get("release_date") else None
        ))
        
    return DataResponse(
        data=mapped_movies,
        meta=MetaInfo(total=results.get("total_results", 0))
    )

@router.get("/{movie_id}", response_model=DataResponse[MovieSchema])
async def get_movie(
    movie_id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session)
):
    """Get detailed movie information from our database."""
    movie_service = MovieService(db)
    movie = await movie_service.get_movie(movie_id)
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
        
    return DataResponse(data=MovieSchema.model_validate(movie))

@router.get("/tmdb/{tmdb_id}", response_model=DataResponse[MovieSchema])
async def fetch_and_save_movie_by_tmdb_id(
    tmdb_id: str,
    db: AsyncSession = Depends(get_db_session)
):
    """Fetch movie by TMDB ID, save to DB, and return canonical resource."""
    movie_service = MovieService(db)
    movie = await movie_service.get_or_fetch_movie_by_tmdb_id(tmdb_id)
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found in provider")
        
    return DataResponse(data=MovieSchema.model_validate(movie))
