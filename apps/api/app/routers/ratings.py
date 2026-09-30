from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import uuid
from typing import List

from apps.api.app.dependencies.db import get_db_session
from apps.api.app.dependencies.auth import get_current_user
from cinerec.infrastructure.db.models.user import User
from cinerec.infrastructure.db.models.activity import Rating
from cinerec.core.api import DataResponse
from cinerec.application.schemas.rating import RatingSchema, RatingCreateUpdate

router = APIRouter()

@router.get("/movies/{movie_id}", response_model=DataResponse[RatingSchema])
async def get_movie_rating(
    movie_id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
):
    stmt = select(Rating).where(Rating.user_id == current_user.id, Rating.movie_id == movie_id)
    result = await db.execute(stmt)
    rating = result.scalars().first()
    
    if not rating:
        raise HTTPException(status_code=404, detail="Rating not found")
        
    return DataResponse(data=RatingSchema.model_validate(rating))

@router.put("/movies/{movie_id}", response_model=DataResponse[RatingSchema])
async def set_movie_rating(
    movie_id: uuid.UUID,
    payload: RatingCreateUpdate,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
):
    if not (1.0 <= payload.rating <= 5.0):
        raise HTTPException(status_code=400, detail="Rating must be between 1.0 and 5.0")
        
    stmt = select(Rating).where(Rating.user_id == current_user.id, Rating.movie_id == movie_id)
    result = await db.execute(stmt)
    rating = result.scalars().first()
    
    if rating:
        rating.rating = payload.rating
    else:
        rating = Rating(user_id=current_user.id, movie_id=movie_id, rating=payload.rating)
        db.add(rating)
        
    await db.commit()
    await db.refresh(rating)
    
    return DataResponse(data=RatingSchema.model_validate(rating))

@router.delete("/movies/{movie_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_movie_rating(
    movie_id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
):
    stmt = select(Rating).where(Rating.user_id == current_user.id, Rating.movie_id == movie_id)
    result = await db.execute(stmt)
    rating = result.scalars().first()
    
    if rating:
        await db.delete(rating)
        await db.commit()
