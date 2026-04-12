from datetime import datetime
from typing import List
from pydantic import BaseModel, Field, computed_field

from src.lib.utils.base_entity import BaseEntity
from src.lib.utils.pagination import Page


class CreateSimulationDevice(BaseModel):
    device_id: str = Field(..., description="The id of the device")
    name: str = Field(..., description="The that owns the device")
    latitude: float = Field(..., description="The latitude of the device location")
    longitude: float = Field(..., description="The longitude of the device location")
    simulation_id: str = Field(..., description="The id of the simulation")


    @computed_field
    @property
    def created_at(self) -> datetime:
        return datetime.now()
    
    @computed_field
    @property
    def updated_at(self) -> datetime:
        return datetime.now()


class SimulationDevice(BaseEntity):
    device_id: str = Field(..., description="The id of the device")
    name: str = Field(..., description="The that owns the device")
    latitude: float = Field(..., description="The latitude of the device location")
    longitude: float = Field(..., description="The longitude of the device location")
    simulation_id: str = Field(..., description="The id of the simulation")
    

class ListSimulationDevices(Page):
    simulation_id: str = Field(..., description="The id of the simulation")
