import uuid
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, not_

from cinerec.infrastructure.db.models.movie import Movie
from cinerec.infrastructure.db.models.activity import Rating, Watchlist, ViewingHistory
from cinerec.infrastructure.db.models.memory import Memory
from cinerec.application.schemas.movie import MovieSchema

class RecommendationService:
    def __init__(self, session: AsyncSession):
        self.session = session
        
    async def get_popularity_baseline(self, limit: int = 20, exclude_user_id: Optional[uuid.UUID] = None) -> List[Movie]:
        """
        Baseline 1: Popularity (simulated via rating count and average score).
        Excludes movies the user has already seen/rated if user_id is provided.
        """
        # Exclude subquery
        excluded_movie_ids = []
        if exclude_user_id:
            stmt = select(Rating.movie_id).where(Rating.user_id == exclude_user_id)
            result = await self.session.execute(stmt)
            excluded_movie_ids.extend(result.scalars().all())
            
            stmt = select(ViewingHistory.movie_id).where(ViewingHistory.user_id == exclude_user_id)
            result = await self.session.execute(stmt)
            excluded_movie_ids.extend(result.scalars().all())

        # Base query (in a real system, popularity is materialized or derived from real stats)
        # We will approximate by selecting recent high-profile movies
        stmt = select(Movie)
        
        if excluded_movie_ids:
            stmt = stmt.where(not_(Movie.id.in_(excluded_movie_ids)))
            
        # Fallback to random order or release date for now if rating aggregates aren't materialized
        stmt = stmt.order_by(Movie.release_date.desc().nulls_last()).limit(limit)
        
        result = await self.session.execute(stmt)
        return result.scalars().all()
        
    async def get_rule_based_personalization(self, user_id: uuid.UUID, limit: int = 20) -> List[Movie]:
        """
        Baseline 2: Rule-based using explicit memories.
        E.g. If user explicitly likes 'Sci-Fi', boost Sci-Fi.
        """
        # Fetch active explicit memories
        stmt = select(Memory).where(
            Memory.user_id == user_id,
            Memory.status == "ACTIVE",
            Memory.polarity == "POSITIVE",
            Memory.memory_type == "GENRE"
        )
        result = await self.session.execute(stmt)
        liked_genres = [m.subject for m in result.scalars().all()]
        
        # If no preferences, fallback to popularity
        if not liked_genres:
            return await self.get_popularity_baseline(limit=limit, exclude_user_id=user_id)
            
        # Exclude seen
        stmt = select(Rating.movie_id).where(Rating.user_id == user_id)
        result = await self.session.execute(stmt)
        excluded_movie_ids = result.scalars().all()
        
        # This is a naive approximation since genre mapping involves junction tables
        # For the baseline, we just use popularity fallback.
        # A true implementation would join movie_genres.
        return await self.get_popularity_baseline(limit=limit, exclude_user_id=user_id)

    async def get_collaborative_filtering_recommendations(self, user_id: uuid.UUID, limit: int = 20) -> List[Movie]:
        """
        Baseline 3: Collaborative Filtering (Item-Item / Matrix Factorization).
        In Phase 13, this orchestrates the behavioral recommendation signals.
        For now, this is a stub that falls back to rule-based.
        """
        # In a real implementation, this would:
        # 1. Fetch user's implicit/explicit history
        # 2. Query a pre-computed item-item similarity matrix (e.g. from Redis) or ANN index.
        # 3. Rank candidates.
        return await self.get_rule_based_personalization(user_id=user_id, limit=limit)

    async def get_hybrid_recommendations(self, user_id: uuid.UUID, limit: int = 20) -> List[Movie]:
        """
        Phase 14: Hybrid Recommendation Engine.
        Combines Semantic, Collaborative, and Rule-based candidates.
        """
        # Fetch candidates from various sources
        cf_candidates = await self.get_collaborative_filtering_recommendations(user_id=user_id, limit=limit)
        rule_candidates = await self.get_rule_based_personalization(user_id=user_id, limit=limit)
        
        # In a real system, you'd fetch semantic candidates from vector_service here
        
        # Combine and deduplicate
        seen_ids = set()
        hybrid_list = []
        
        # Simple round-robin or scoring logic
        for candidate in cf_candidates + rule_candidates:
            if candidate.id not in seen_ids:
                seen_ids.add(candidate.id)
                hybrid_list.append(candidate)
                if len(hybrid_list) >= limit:
                    break
                    
        return hybrid_list

    async def get_recommendations(self, user_id: uuid.UUID, context: Optional[dict] = None, limit: int = 20) -> List[Movie]:
        """Master orchestrator for recommendation baselines."""
        return await self.get_hybrid_recommendations(user_id=user_id, limit=limit)
