from pydantic import BaseModel, Field, field_validator
from typing_extensions import Annotated, Optional
from enum import Enum
from pymongo import ASCENDING, DESCENDING


class Sort(Enum):
    """Enumeration of sort order options."""
    ASC = 'asc'
    DESC = 'desc'


sort_mapping = {
    Sort.ASC: ASCENDING,
    Sort.DESC: DESCENDING,
}
"""Mapping of Sort enum values to MongoDB sort constants."""


class Page(BaseModel):
    """Base model for pagination parameters.

    Provides common pagination and sorting fields for list endpoints.

    Attributes:
        limit: Maximum number of items to return per page
        skip: Number of items to skip before returning results
        sort: Sort order for results (ascending or descending)
        query: Optional search query string for filtering
    """
    limit: Annotated[int, Field(10, gt=0, description='The number of items for the page')]
    skip: Annotated[int, Field(0, description='The no of items to skip')]
    sort: Annotated[Sort, Field(Sort.ASC, description='The order to sort items')]
    query: Optional[str] = Field(None, description="Search query for filtering items")
    