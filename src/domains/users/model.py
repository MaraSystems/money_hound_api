from pydantic import EmailStr, Field
from typing import Annotated
from datetime import datetime

from src.lib.utils.base_entity import BaseEntity
from ...lib.utils.pagination import Page


class User(BaseEntity):
    email: EmailStr = Field(..., description="Email address of the user")
    firstname: str = Field(..., description="First name of the user")
    lastname: str = Field(..., description="Last name of the user")


class ListUsers(Page):
    query: Annotated[str, Field('')]