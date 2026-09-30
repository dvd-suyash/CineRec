import asyncio
from apps.worker.worker import celery_app

@celery_app.task(bind=True, max_retries=3)
def ingest_tmdb_movie(self, tmdb_id: str):
    """
    Background task to async fetch and normalize a movie from TMDB.
    Runs an asyncio event loop since the main app is async.
    """
    from apps.api.app.dependencies.db import AsyncSessionLocal
    from cinerec.application.movie_service import MovieService
    
    async def run():
        async with AsyncSessionLocal() as session:
            service = MovieService(session)
            await service.get_or_fetch_movie_by_tmdb_id(tmdb_id)
            
    asyncio.run(run())
    return {"status": "success", "tmdb_id": tmdb_id}

@celery_app.task
def generate_taste_profile(user_id: str):
    """
    Background task to analyze memory and behavioral history
    to generate/update a user's Taste Profile.
    """
    pass # Stub for Phase 16
