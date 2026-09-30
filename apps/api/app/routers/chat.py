import uuid
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.app.dependencies.db import get_db_session
from apps.api.app.dependencies.auth import get_current_user
from cinerec.infrastructure.db.models.user import User
from cinerec.application.conversation_service import ConversationService
from cinerec.core.api import DataResponse

router = APIRouter()

class ChatRequest(BaseModel):
    message: str

class SessionResponse(BaseModel):
    session_id: uuid.UUID

@router.post("/sessions", response_model=DataResponse[SessionResponse])
async def create_chat_session(
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
):
    service = ConversationService(db)
    session = await service.create_session(current_user.id)
    return DataResponse(data=SessionResponse(session_id=session.id))

@router.post("/sessions/{session_id}/message")
async def send_message(
    session_id: uuid.UUID,
    payload: ChatRequest,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
):
    """
    Send a message and receive a Server-Sent Events (SSE) stream of the assistant's response.
    """
    service = ConversationService(db)
    
    return StreamingResponse(
        service.chat(session_id, current_user.id, payload.message),
        media_type="text/event-stream"
    )
