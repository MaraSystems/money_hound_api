from datetime import datetime
from decimal import Decimal
from typing import Literal, Optional
from pydantic import Field
from src.models.entity import Creator, Entity
from src.models.pagination import Page

JobCategory = Literal["FULL_TIME", "PART_TIME", "CONTRACT"]
JobStatus = Literal["OPEN", "FILLED", "CLOSED", "TERMINATED"]

class Job(Entity):
    title: str = Field(..., description="The title of the job")
    organization_id: str = Field(..., description="The organization that created the job")
    branch_id: str = Field(..., description="The branch of the organizatioino that created the job")
    salary: Decimal = Field(..., description="The salary for the job")
    categgry: JobCategory = Field(..., description="The category of the job")
    status: JobStatus = Field(..., description="The status of the job")
    filled_at: Optional[datetime] = Field(..., description="The date the job was filled")
    terminated_at: Optional[datetime] = Field(..., description="The date the job was filled")


class CreateJob(Creator):
    title: str = Field(..., description="The title of the job")
    organization_id: str = Field(..., description="The organization that created the job")
    branch_id: str = Field(..., description="The branch of the organizatioino that created the job")
    salary: Decimal = Field(..., description="The salary for the job")
    categgry: JobCategory = Field(..., description="The category of the job")
    status: JobStatus = "OPEN"


class ListJob(Page):
    simulation_id: str = Field(..., description="The id of the simulation")
