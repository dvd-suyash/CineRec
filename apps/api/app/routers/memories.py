from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
import uuid
from typing import List, Optional
from pydantic import BaseModel, ConfigDict
from datetime import datetime

from apps.api.app.dependencies.db import get_db_session
from apps.api.app.dependencies.auth import get_current_user
from cinerec.infrastructure.db.models.user import User
from cinerec.application.memory_service import MemoryService
from cinerec.core.api import DataResponse

router = APIRouter()

class MemorySchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: uuid.UUID
    memory_type: str
    subject: str
    value: Optional[dict] = None
    polarity: str
    confidence: float
    source: str
    status: str
    evidence_count: int
    last_evidence_at: Optional[datetime] = None

@router.get("/", response_model=DataResponse[List[MemorySchema]])
async def get_memories(
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
):
    service = MemoryService(db)
    memories = await service.get_active_memories(current_user.id)
    return DataResponse(data=[MemorySchema.model_validate(m) for m in memories])

@router.delete("/{memory_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_memory(
    memory_id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
):
    service = MemoryService(db)
    success = await service.delete_memory(current_user.id, memory_id)
    if not success:
        raise HTTPException(status_code=404, detail="Memory not found")
