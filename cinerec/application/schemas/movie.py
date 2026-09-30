import uuid
from typing import Optional
from datetime import date
from pydantic import BaseModel, ConfigDict

class MovieSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    original_title: Optional[str] = None
    overview: Optional[str] = None
    release_date: Optional[date] = None
    release_year: Optional[int] = None
    runtime_minutes: Optional[int] = None
    original_language: Optional[str] = None
    poster_path: Optional[str] = None
    backdrop_path: Optional[str] = None
    adult_content: bool = False
    status: Optional[str] = None
