import uuid
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict

class InteractionCreate(BaseModel):
    movie_id: Optional[uuid.UUID] = None
    event_type: str # e.g. search, movie_view, movie_click, recommendation_impression, skip, like, dislike
    session_id: Optional[uuid.UUID] = None
    position: Optional[int] = None
    surface: Optional[str] = None
    metadata: Optional[dict] = None

class InteractionSchema(InteractionCreate):
    model_config = ConfigDict(from_attributes=True)
    
    id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime
