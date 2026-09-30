from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from apps.api.app.dependencies.db import get_db_session
from apps.api.app.dependencies.auth import get_current_user
from cinerec.infrastructure.db.models.user import User
from cinerec.application.interaction_service import InteractionService
from cinerec.application.schemas.interaction import InteractionSchema, InteractionCreate
from cinerec.core.api import DataResponse

router = APIRouter()

@router.post("/", response_model=DataResponse[InteractionSchema])
async def track_interaction(
    payload: InteractionCreate,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
):
    """Record a telemetry/behavioral event for a user."""
    service = InteractionService(db)
    interaction = await service.track_event(current_user.id, payload)
    return DataResponse(data=InteractionSchema.model_validate(interaction))
