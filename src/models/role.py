from datetime import datetime
from pydantic import BaseModel, Field, computed_field, field_validator
from typing import List, Optional

from src.lib.utils.base_entity import BaseEntity
from src.lib.utils.pagination import Page


class CreateRole(BaseModel):
    title: str = Field(..., description="Title of the role")
    description: Optional[str] = Field(None, description="Description of the role")
    permissions: List[str] = Field(..., description="List of permissions associated with the role")

    @computed_field
    @property
    def created_at(self) -> datetime:
        return datetime.now()
    

    @computed_field
    @property
    def updated_at(self) -> datetime:
        return datetime.now()


    @computed_field
    @property
    def hidden(self) -> bool:
        return False


    @computed_field
    @property
    def users(self) -> List:
        return []
    

class UpdateRole(BaseModel):
    title: Optional[str] = Field(None, description="Title of the role")
    description: Optional[str] = Field(None, description="Description of the role")
    permissions: Optional[List[str]] = Field(None, description="List of permissions associated with the role")

    @computed_field
    @property
    def updated_at(self) -> datetime:
        return datetime.now()


class ListRoles(Page):
    query: Optional[str] = Field(None, description="Search query for filtering roles")
    user_id: Optional[str] = Field(None, description="Id of the user the roles belong to")


class Role(BaseEntity):
    title: str = Field(..., description="Title of the role")
    description: Optional[str] = Field(None, description="Description of the role")
    permissions: List[str] = Field(..., description="List of permissions associated with the role")
    author_id: str = Field(..., description="Unique identifier of the author who created the role")

    users: List[str] = Field(..., description="List of users assigned to this role")


class Domain(BaseModel):
    name: str = Field(..., description="Name of the domain")
    subdomains: List[str] = Field(..., description="List of subdomains under the domain")