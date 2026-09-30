from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from apps.api.app.dependencies.db import get_db_session
from apps.api.app.dependencies.auth import get_current_user
from cinerec.infrastructure.db.models.user import User
from cinerec.application.recommendation_service import RecommendationService
from cinerec.application.schemas.movie import MovieSchema
from cinerec.core.api import DataResponse

router = APIRouter()

@router.get("/baseline", response_model=DataResponse[List[MovieSchema]])
async def get_baseline_recommendations(
    limit: int = 20,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
):
    service = RecommendationService(db)
    movies = await service.get_recommendations(current_user.id, limit=limit)
    return DataResponse(data=[MovieSchema.model_validate(m) for m in movies])
