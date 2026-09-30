from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from apps.api.app.dependencies.db import get_db_session
from apps.api.app.dependencies.auth import get_current_user
from cinerec.infrastructure.db.models.user import User
from cinerec.infrastructure.db.models.activity import Watchlist
from cinerec.infrastructure.db.models.movie import Movie, MovieProviderId
from cinerec.infrastructure.db.models.memory import UserMemory
from cinerec.core.api import DataResponse

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
                "title": movie.title,
                "year": movie.release_year or "",
                "poster": f"https://image.tmdb.org/t/p/w500{movie.poster_path}" if movie.poster_path else None
            })

    # 2. Fetch Memories
    stmt_memories = select(UserMemory).where(UserMemory.user_id == current_user.id).order_by(UserMemory.created_at.desc()).limit(3)
    result_memories = await db.execute(stmt_memories)
    memories_data = [m.content for m in result_memories.scalars().all()]
    
    if not memories_data:
        memories_data = ["Arachne is watching. Your cinematic essence is still forming."]

    # 3. DNA (Mock for now, will aggregate genre preferences later)
    dna_data = [
        {"trait": "Atmospheric Dread", "percentage": 95},
        {"trait": "Surrealism", "percentage": 82},
        {"trait": "Neon Noir", "percentage": 78},
        {"trait": "Psychological Horror", "percentage": 70},
        {"trait": "Slow Burn", "percentage": 65},
    ]

    return DataResponse(data={
        "watchlist": watchlist_data,
        "memories": memories_data,
        "dna": dna_data,
        "fixation": {
            "name": "Denis Villeneuve",
            "type": "DIRECTOR",
            "stat": "5 Films Discussed",
            "image": "https://image.tmdb.org/t/p/original/rMziD3VIfA1sE1YIDJ9Q0pD5oPj.jpg"
        }
    })
