from pydantic import EmailStr, Field
from typing_extensions import Annotated

from src.models.entity import Entity
from src.models.pagination import Page


class User(Entity):
    email: EmailStr = Field(..., description="Email address of the user")
    firstname: str = Field(..., description="First name of the user")
    lastname: str = Field(..., description="Last name of the user")


class ListUsers(Page):
    query: Annotated[str, Field('')]