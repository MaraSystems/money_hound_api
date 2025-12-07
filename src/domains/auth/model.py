from datetime import datetime
from fastapi import Depends
from pydantic import BaseModel, EmailStr, Field, computed_field, field_validator
from typing import Annotated, List, Optional

from pymongo.database import Database

from src.config.database import get_db
from src.domains.roles.model import Role


class CreateUser(BaseModel):
    email: EmailStr = Field(..., description="Email address of the user")
    firstname: Annotated[str, Field(min_length=3, description="First name of the user")]
    lastname: Annotated[str, Field(min_length=3, description="Last name of the user")]

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
    

class UpdateProfile(BaseModel):
    email: Optional[EmailStr] = Field(None, description="Email address of the user")
    firstname: Optional[str] = Field(None, min_length=3, description="First name of the user")
    lastname: Optional[str] = Field(None, min_length=3, description="Last name of the user")

    @computed_field
    @property
    def updated_at(self) -> datetime:
        return datetime.now()


class TokenData(BaseModel):
    sub: str


class Token(BaseModel):
    token: str = Field(..., description="JWT access token")
    access: str = Field(..., description="Access level of the token")


class RequestOTP(BaseModel):
    email: EmailStr = Field(..., description="Email address of the user")


class VerifyOTP(RequestOTP):
    code: str = Field(..., description="One-time password (OTP) code")
    

class CurrentUser(BaseModel):
    id: str = Field(..., description="Unique identifier for the user")
    email: EmailStr = Field(..., description="Email address of the user")


    async def get_permissions(self, db: Database) -> List[str]:
        roles = await db.roles.find({'users': self.id}).to_list()
        return [p for r in roles for p in r['permissions']]