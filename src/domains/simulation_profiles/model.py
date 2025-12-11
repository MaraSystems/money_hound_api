from datetime import datetime
from typing import List
from uuid import uuid4
from pydantic import BaseModel, Field, computed_field

from src.lib.utils.base_entity import BaseEntity
from src.lib.utils.pagination import Page


class CreateSimulationProfile(BaseModel):
    user_id: str = Field(default_factory=lambda: f"USER_{str(uuid4())}", description="The id of the user")
    name: str = Field(..., description="The name of the user")
    gender: str = Field(..., description="The gender of the user")
    email: str = Field(..., description="The email of the user")
    birthdate: datetime = Field(..., description="The date of birth of the user")
    devices: List[str] = Field(..., description="The devices for the user")
    latitude: float = Field(..., description="The latitude of the user location")
    longitude: float = Field(..., description="The longitude of the user location")
    simulation_id: str = Field(..., description="The id of the simulation")

    @computed_field
    @property
    def created_at(self) -> datetime:
        return datetime.now()
    
    @computed_field
    @property
    def updated_at(self) -> datetime:
        return datetime.now()


class SimulationProfile(BaseEntity):
    user_id: str = Field(..., description="The id of the user")
    name: str = Field(..., description="The name of the user")
    gender: str = Field(..., description="The gender of the user")
    email: str = Field(..., description="The email of the user")
    birthdate: datetime = Field(..., description="The date of birth of the user")
    devices: List[str] = Field(..., description="The devices for the user")
    latitude: float = Field(..., description="The latitude of the user location")
    longitude: float = Field(..., description="The longitude of the user location")
    simulation_id: str = Field(..., description="The id of the simulation")
    

class ListSimulationProfiles(Page):
    simulation_id: str = Field(..., description="The id of the simulation")
