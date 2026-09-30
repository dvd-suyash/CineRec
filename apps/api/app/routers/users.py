from fastapi import APIRouter, Depends
from typing import Optional
from pydantic import BaseModel
import uuid

from cinerec.infrastructure.db.models.user import User
from apps.api.app.dependencies.auth import get_current_user

router = APIRouter()

class UserResponse(BaseModel):
    id: uuid.UUID
    display_name: str
    avatar_url: Optional[str]
    locale: str
    region_code: str
    onboarding_status: str

    model_config = {"from_attributes": True}

@router.get("/me", response_model=UserResponse)
async def read_users_me(
    current_user: User = Depends(get_current_user)
):
    """
    Get current user profile (Phase 4 requirement)
    """
    return current_user
