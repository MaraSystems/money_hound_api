from datetime import datetime
from pydantic import BaseModel, Field, field_validator

class BaseEntity(BaseModel):
    id: str = Field(alias="_id", description="Unique identifier")
    created_at: datetime = Field(..., description="Timestamp when created")
    updated_at: datetime = Field(..., description="Timestamp when last updated")

    
    @field_validator("id", mode="before")
    def convert_objectid(cls, v):
        return str(v)

    model_config = {
        "populate_by_name": True,       
        "arbitrary_types_allowed": True
    }