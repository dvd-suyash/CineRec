from typing import Generic, TypeVar, Optional, Any
from pydantic import BaseModel

T = TypeVar("T")

class MetaInfo(BaseModel):
    total: Optional[int] = None
    next_cursor: Optional[str] = None
    has_more: Optional[bool] = None

class DataResponse(BaseModel, Generic[T]):
    data: T
    meta: Optional[MetaInfo] = None

class ErrorResponse(BaseModel):
    error: str
    details: Optional[Any] = None
