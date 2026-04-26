from pydantic import BaseModel, Field

class SimulationLocation(BaseModel):
    latitude: float = Field(..., description="The latitude of the individual location")
    longitude: float = Field(..., description="The longitude of the individual location")