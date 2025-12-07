from datetime import datetime
from typing import Annotated, Literal
from pydantic import BaseModel, Field, computed_field
from uuid import uuid4

from src.lib.utils.base_entity import BaseEntity
from src.lib.utils.pagination import Page


class CreateChat(BaseModel):
    message: str = Field(..., description="User query")
    session_id: str = Field(default=str(uuid4()))
    role: Literal['human', 'bot'] = Field(default='human')

    @computed_field
    @property
    def created_at(self) -> datetime:
        return datetime.now()
    
    @computed_field
    @property
    def updated_at(self) -> datetime:
        return datetime.now()


class Chat(BaseEntity):
    message: str = Field(...)
    session_id: str = Field(...)
    role: Literal['human', 'bot']
