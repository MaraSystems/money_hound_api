from typing_extensions import Generic, TypeVar, Optional
from pydantic import BaseModel

T = TypeVar("T")

class DataResponse(BaseModel, Generic[T]):
    success: bool = True
    data: Optional[T] = None
    message: Optional[str] = None
