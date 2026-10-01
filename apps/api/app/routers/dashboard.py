from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from apps.api.app.dependencies.auth import get_current_user
from apps.api.app.dependencies.db import get_db_session
from cinerec.core.api import DataResponse
from cinerec.infrastructure.db.models.activity import ViewingHistory, Watchlist
from cinerec.infrastructure.db.models.memory import Memory
from cinerec.infrastructure.db.models.movie import Movie
from cinerec.infrastructure.db.models.user import User

router = APIRouter()

@router.get("/", response_model=DataResponse)
async def get_dashboard(
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
):
    # 1. Fetch Watchlist
    stmt_watchlist = select(Watchlist, Movie).join(Movie, Watchlist.movie_id == Movie.id)\
        .options(selectinload(Movie.provider_ids))\
        .where(Watchlist.user_id == current_user.id)\
        .order_by(Watchlist.created_at.desc()).limit(10)
    result_watchlist = await db.execute(stmt_watchlist)

    watchlist_data = []
    for wl, movie in result_watchlist.all():
        tmdb_id = None
        for pid in movie.provider_ids:
            if pid.provider == "tmdb":
                tmdb_id = pid.external_id
                break

        if tmdb_id:
            watchlist_data.append({
                "id": int(tmdb_id),
                "db_id": str(movie.id),
                "title": movie.title,
                "year": movie.release_year or "",
                "poster": f"https://image.tmdb.org/t/p/w500{movie.poster_path}" if movie.poster_path else None
            })

    # 2. Fetch History
    stmt_history = select(ViewingHistory, Movie).join(Movie, ViewingHistory.movie_id == Movie.id)\
        .options(selectinload(Movie.provider_ids))\
        .where(ViewingHistory.user_id == current_user.id)\
        .order_by(ViewingHistory.completed_at.desc().nulls_last()).limit(10)
    result_history = await db.execute(stmt_history)

    history_data = []
    for hist, movie in result_history.all():
        tmdb_id = None
        for pid in movie.provider_ids:
            if pid.provider == "tmdb":
                tmdb_id = pid.external_id
                break

        if tmdb_id:
            history_data.append({
                "id": int(tmdb_id),
                "db_id": str(movie.id),
                "title": movie.title,
                "year": movie.release_year or "",
                "poster": f"https://image.tmdb.org/t/p/w500{movie.poster_path}" if movie.poster_path else None
            })

    # 3. Fetch Memories
    stmt_memories = select(Memory).where(Memory.user_id == current_user.id).order_by(Memory.created_at.desc()).limit(3)
    result_memories = await db.execute(stmt_memories)
    memories_data = [m.value for m in result_memories.scalars().all()]

    if not memories_data:
        memories_data = ["Arachne is watching. Your cinematic essence is still forming."]

    # 4. Total Stats (replaces mock fixation if empty)
    stmt_wl_count = select(func.count()).select_from(Watchlist).where(Watchlist.user_id == current_user.id)
    wl_count = await db.scalar(stmt_wl_count)

    stmt_hist_count = select(func.count()).select_from(ViewingHistory).where(ViewingHistory.user_id == current_user.id)
    hist_count = await db.scalar(stmt_hist_count)

    return DataResponse(data={
        "watchlist": watchlist_data,
        "history": history_data,
        "memories": memories_data,
        "stats": {
            "watchlist_count": wl_count or 0,
            "history_count": hist_count or 0
        }
    })
