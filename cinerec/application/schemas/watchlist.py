import uuid
from typing import List
from pydantic import BaseModel, ConfigDict
from datetime import datetime
from cinerec.application.schemas.movie import MovieSchema

class WatchlistSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    user_id: uuid.UUID
    movie_id: uuid.UUID
    created_at: datetime
