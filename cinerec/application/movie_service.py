from typing import Optional, Dict, Any, List
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime

from cinerec.infrastructure.db.models import Movie, MovieProviderId
from cinerec.domain.movie.provider import MovieDataProvider
from cinerec.infrastructure.tmdb.adapter import TMDBAdapter

class MovieService:
    def __init__(self, session: AsyncSession, provider: Optional[MovieDataProvider] = None):
        self.session = session
        # Default to TMDB adapter if none provided
        self.provider = provider or TMDBAdapter()

    async def get_movie(self, movie_id: uuid.UUID) -> Optional[Movie]:
        """Get normalized movie strictly from the database."""
        stmt = select(Movie).where(Movie.id == movie_id)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_or_fetch_movie_by_tmdb_id(self, tmdb_id: str, language: str = "en-US") -> Optional[Movie]:
        """
        Cache-aside equivalent for the database:
        Check DB first using provider ID mapping. If missing, fetch from TMDB, normalize, and save.
        """
        # 1. Check if we already have it mapped in the database
        stmt = select(Movie).join(MovieProviderId).where(
            MovieProviderId.provider == "tmdb",
            MovieProviderId.external_id == str(tmdb_id)
        )
        result = await self.session.execute(stmt)
        movie = result.scalars().first()
        
        if movie:
            return movie
            
        # 2. Not in DB. Fetch from provider (which hits Redis then TMDB).
        tmdb_data = await self.provider.get_movie(tmdb_id, language=language)
        if not tmdb_data:
            return None
            
        # 3. Normalize and save to DB
        return await self._normalize_and_save_movie(tmdb_data, tmdb_id)

    async def _normalize_and_save_movie(self, tmdb_data: Dict[str, Any], tmdb_id: str) -> Movie:
        # Extract release date safely
        release_date = None
        release_year = None
        if tmdb_data.get("release_date"):
            try:
                release_date = datetime.strptime(tmdb_data["release_date"], "%Y-%m-%d").date()
                release_year = release_date.year
            except ValueError:
                pass
                
        # Create Movie entity
        movie = Movie(
            title=tmdb_data.get("title") or tmdb_data.get("original_title", "Unknown"),
            original_title=tmdb_data.get("original_title"),
            overview=tmdb_data.get("overview"),
            release_date=release_date,
            release_year=release_year,
            runtime_minutes=tmdb_data.get("runtime"),
            original_language=tmdb_data.get("original_language"),
            poster_path=tmdb_data.get("poster_path"),
            backdrop_path=tmdb_data.get("backdrop_path"),
            adult_content=tmdb_data.get("adult", False),
            status=tmdb_data.get("status")
        )
        self.session.add(movie)
        await self.session.flush() # Get movie.id
        
        # Link provider ID
        provider_id = MovieProviderId(
            movie_id=movie.id,
            provider="tmdb",
            external_id=str(tmdb_id)
        )
        self.session.add(provider_id)
        
        # In a complete implementation, we'd also normalize Genres, Credits, Keywords here
        
        await self.session.commit()
        await self.session.refresh(movie)
        return movie
