from datetime import datetime
from pydantic import BaseModel, Field, computed_field, field_validator


class Update(BaseModel):
    """Base model for editing an entity.

    Provides automatic updated_at timestamp for modifications.
    """

    @computed_field
    @property
    def updated_at(self) -> datetime:
        """Return current datetime as the updated timestamp."""
        return datetime.now()


class Creator(Update):
    """Base model for creating an entity.

    Extends Update with automatic created_at and hidden fields.
    """

    @computed_field
    @property
    def created_at(self) -> datetime:
        """Return current datetime as the created timestamp."""
        return datetime.now()

    @computed_field
    @property
    def hidden(self) -> bool:
        """Return default hidden status (False for new entities)."""
        return False


class Entity(BaseModel):
    """Base model for all database entities.

    Provides common fields and configuration for MongoDB documents.

    Attributes:
        id: Unique identifier (aliased from _id for MongoDB)
        created_at: Timestamp when entity was created
        updated_at: Timestamp when entity was last updated
    """
    id: str = Field(alias="_id", description="Unique identifier")
    created_at: datetime = Field(..., description="Timestamp when created")
    updated_at: datetime = Field(..., description="Timestamp when last updated")

    @field_validator("id", mode="before")
    def convert_objectid(cls, v):
        """Convert MongoDB ObjectId to string."""
        return str(v)

    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }