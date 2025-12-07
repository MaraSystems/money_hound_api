from datetime import datetime
from typing import Literal, Optional
from pydantic import BaseModel, Field, computed_field

from src.lib.utils.base_entity import BaseEntity
from src.lib.utils.pagination import Page


class CreateSimulation(BaseModel):
    num_banks: int = Field(..., description="The number of banks")
    min_num_user: int = Field(..., description="The min number of users")
    latitude: float = Field(..., description="The latitude of the simulation")
    longitude: float = Field(..., description="The longitude of the simulation")
    radius: int = Field(10_000, description="The radius of the simulation")
    fraudulence: Optional[float] = Field(0.05, description="The percentage of fraudulence")
    min_amount: Optional[float] = Field(100, description="The min amount to be generated")
    max_amount: Optional[float] = Field(100_000_000_000, description="The maximium amount to be generated")
    days: Optional[float] = Field(7, description="The number of days to simulate")
    

    @computed_field
    @property
    def status(self) -> Literal['PENDING', 'COMPLETE', 'FAILED']:
        return 'PENDING'

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

class Simulation(BaseEntity):
    num_banks: int = Field(..., description="The number of banks")
    min_num_user: int = Field(..., description="The min number of users")
    fraudulence: float = Field(..., description="The percentage of fraudulence")
    latitude: float = Field(..., description="The latitude of the simulation")
    longitude: float = Field(..., description="The longitude of the simulation")
    radius: int = Field(..., description="The radius of the simulation")
    min_amount: float = Field(..., description="The min amount to be generated")
    max_amount: float = Field(..., description="The maximium amount to be generated")
    author_id: str = Field(..., description="Unique identifier of the author who created the simulation")
    status: Literal['PENDING', 'COMPLETE', 'FAILED'] = Field(..., description="The status of the simulation")
    days: float = Field(..., description="The number of days to simulate")

class ListSimulations(Page):
    author_id: Optional[str] = Field(None, description="Unique identifier of the author who created the simulation")


class UpdateSimulation(BaseModel):
    num_banks: Optional[int] = Field(None, description="The number of banks")
    min_num_user: Optional[int] = Field(None, description="The min number of users")
    fraudulence: Optional[float] = Field(None, description="The percentage of fraudulence")
    latitude: Optional[float] = Field(None, description="The latitude of the simulation")
    longitude: Optional[float] = Field(None, description="The longitude of the simulation")
    radius: Optional[int] = Field(None, description="The radius of the simulation")
    min_amount: Optional[float] = Field(None, description="The min amount to be generated")
    max_amount: Optional[float] = Field(None, description="The maximium amount to be generated")
    days: Optional[float] = Field(None, description="The number of days to simulate")

    @computed_field
    @property
    def updated_at(self) -> datetime:
        return datetime.now()

    ...