from pydantic import BaseModel, Field, field_validator
from typing import Annotated, Optional
from enum import Enum
from pymongo import ASCENDING, DESCENDING


class Sort(Enum):
    ASC = 'asc'
    DESC = 'desc'


sort_mapping = {
    Sort.ASC: ASCENDING,
    Sort.DESC: DESCENDING,
}


class Page(BaseModel):
    limit: Annotated[int, Field(10, gt=0, description='The number of items for the page')]
    skip: Annotated[int, Field(0, description='The no of items to skip')]
    sort: Annotated[Sort, Field(Sort.ASC, description='The order to sort items')]
    query: Optional[str] = Field(None, description="Search query for filtering items")
    