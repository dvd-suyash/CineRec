import uuid
from typing import Optional
from pydantic import BaseModel, ConfigDict
from datetime import datetime

class RatingSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: uuid.UUID
    movie_id: uuid.UUID
    rating: float
    created_at: datetime
    updated_at: datetime

class RatingCreateUpdate(BaseModel):
    rating: float
