from datetime import datetime
from typing_extensions import Literal, Optional
from pydantic import BaseModel, Field, computed_field

from src.lib.utils.base_entity import BaseEntity
from src.models.pagination import Page
from src.models.entity import Creator


DeviceType = Literal["ATM", "MOBILE"]

class CreateSimulationDevice(Creator):
    device_id: str = Field(..., description="The id of the device")
    owner: str = Field(..., description="The owner of the device")
    type: DeviceType = Field(..., description="The type of the device")
    latitude: float = Field(..., description="The latitude of the device location")
    longitude: float = Field(..., description="The longitude of the device location")
    simulation_id: Optional[str] = Field(None, description="The id of the simulation")


class SimulationDevice(BaseEntity):
    device_id: str = Field(..., description="The id of the device")
    owner: str = Field(..., description="The owner of the device")
    type: DeviceType = Field(..., description="The type of the device")
    latitude: float = Field(..., description="The latitude of the device location")
    longitude: float = Field(..., description="The longitude of the device location")
    simulation_id: Optional[str] = Field(None, description="The id of the simulation")
    

class ListSimulationDevices(Page):
    simulation_id: str = Field(..., description="The id of the simulation")
