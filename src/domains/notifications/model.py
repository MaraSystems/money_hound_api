from datetime import datetime
from typing import Annotated, Literal, Optional, List, Dict
from fastapi import HTTPException, status
from pydantic import BaseModel, Field, computed_field, field_validator

from src.lib.utils.base_entity import BaseEntity
from src.lib.utils.pagination import Page


class CreateNotification(BaseModel):
    subject: str = Field(description="Subject of the notification")
    message: str = Field(description="Message of the role")
    category: Literal['info', 'warning', 'alert', 'system', 'message']
    expires_at: Optional[datetime] = Field(None, description="Date the notification expires")
    public: Annotated[bool, Field(True, description='Flag for public notification')]
    parameters: Dict = Field({}, description='Parameters for the notification')


    @field_validator('expires_at')
    @classmethod
    def validate_expiry(cls, value: Optional[datetime]) -> Optional[datetime]:
        if value is None:
            return value

        if value <= datetime.now():
            raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=f'Notification must expire in the future: {value}')

        return value


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
    def users(self) -> List:
        return [] if not self.public else None


    @computed_field
    @property
    def readers(self) -> List:
        return []


class Notification(BaseEntity):
    subject: str = Field(description="Subject of the notification")
    message: str = Field(description="Message of the role")
    category: Literal['info', 'warning', 'alert', 'system', 'message']
    expires_at: Optional[datetime] = Field(None, description="Date the notification expires")
    public: bool = Field(True, description="Flag for public notification")
    parameters: Dict = Field({}, description='Parameters for the notification')

    users: Optional[List[str]] = Field(..., description='List of users to be notified')
    readers: List[str] = Field(..., description='List of users that have been notified')


class ListNotifications(Page):
    query: Optional[str] = Field(None, description="Search query for filtering notification")
