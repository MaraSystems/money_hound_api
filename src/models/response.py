from attrs import validate
from typing_extensions import Generic, TypeVar, Optional
from pydantic import BaseModel, ValidationInfo, computed_field, field_validator

T = TypeVar("T")


class DataResponse(BaseModel, Generic[T]):
    """Generic response model for API responses containing single data item.

    Attributes:
        success: Indicates if the request was successful
        data: Optional data payload of generic type T
        message: Optional status message
    """
    success: bool = True
    data: Optional[T] = None
    message: Optional[str] = None


class PageResponse(DataResponse):
    """Response model for paginated API responses.

    Extends DataResponse with pagination metadata for list responses.

    Attributes:
        skip: Number of items skipped for pagination
        limit: Maximum number of items per page
        data: List of data items
        has_more: Indicates if more items exist beyond current page
    """
    skip: int = 0
    limit: int = 10
    data: Optional[list[T]] = None
    has_more: bool = False