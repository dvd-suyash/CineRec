from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import uuid
from typing import List

from apps.api.app.dependencies.db import get_db_session
from apps.api.app.dependencies.auth import get_current_user
from cinerec.infrastructure.db.models.user import User
from cinerec.infrastructure.db.models.activity import Watchlist
from cinerec.core.api import DataResponse
from cinerec.application.schemas.watchlist import WatchlistSchema

router = APIRouter()

@router.get("/", response_model=DataResponse[List[WatchlistSchema]])
async def get_watchlist(
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
):
    stmt = select(Watchlist).where(Watchlist.user_id == current_user.id).order_by(Watchlist.created_at.desc())
    result = await db.execute(stmt)
    entries = result.scalars().all()
    
    return DataResponse(data=[WatchlistSchema.model_validate(e) for e in entries])

@router.post("/movies/{movie_id}", response_model=DataResponse[WatchlistSchema])
async def add_to_watchlist(
    movie_id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
):
    stmt = select(Watchlist).where(Watchlist.user_id == current_user.id, Watchlist.movie_id == movie_id)
    result = await db.execute(stmt)
    entry = result.scalars().first()
    
    if entry:
        return DataResponse(data=WatchlistSchema.model_validate(entry))
        
    entry = Watchlist(user_id=current_user.id, movie_id=movie_id)
    db.add(entry)
    await db.commit()
    await db.refresh(entry)
    
    return DataResponse(data=WatchlistSchema.model_validate(entry))

@router.delete("/movies/{movie_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_from_watchlist(
    movie_id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
):
    stmt = select(Watchlist).where(Watchlist.user_id == current_user.id, Watchlist.movie_id == movie_id)
    result = await db.execute(stmt)
    entry = result.scalars().first()
    
    if entry:
        await db.delete(entry)
        await db.commit()
