from datetime import datetime
from typing import List
from pydantic import BaseModel, Field, computed_field

from src.lib.utils.base_entity import BaseEntity
from src.lib.utils.pagination import Page


class CreateSimulationBankDevice(BaseModel):
    device_id: str = Field(..., description="The id of the device")
    bank_name: str = Field(..., description="The bank that owns the device")
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


class SimulationBankDevice(BaseEntity):
    device_id: str = Field(..., description="The id of the device")
    bank_name: str = Field(..., description="The bank that owns the device")
    latitude: float = Field(..., description="The latitude of the device location")
    longitude: float = Field(..., description="The longitude of the device location")
    simulation_id: str = Field(..., description="The id of the simulation")
    

class ListSimulationBankDevices(Page):
    simulation_id: str = Field(..., description="The id of the simulation")
