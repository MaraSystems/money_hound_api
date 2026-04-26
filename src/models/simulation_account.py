from uuid import uuid4
from pydantic import Field

from src.models.pagination import Page
from src.models.entity import Creator, Entity


class CreateSimulationAccount(Creator):
    account_no: str = Field(default_factory=lambda: f"ACC_{str(uuid4())[:8]}", description="The account no of the account")    
    account_name: str = Field(..., description="The account name of the account")
    bank_name: str = Field(..., description="The bank_name of the account")
    balance: float = Field(..., description="The balance of the account")
    kyc: int = Field(..., description="The kyc no of the account")
    bvn: str = Field(..., description="The bvn no of the account")
    merchant: bool = Field(..., description="The merchant status of the account")
    opening_device: str = Field(..., description="The device the account was opened with")
    simulation_id: str = Field(..., description="The id of the simulation")


class SimulationAccount(Entity):
    account_no: str = Field(..., description="The account no of the account")
    account_name: str = Field(..., description="The account name of the account")
    bank_name: str = Field(..., description="The bank_name of the account")
    balance: float = Field(..., description="The balance of the account")
    kyc: int = Field(..., description="The kyc no of the account")
    bvn: str = Field(..., description="The bvn no of the account")
    merchant: bool = Field(..., description="The merchant status of the account")
    opening_device: str = Field(..., description="The device the account was opened with")
    simulation_id: str = Field(..., description="The id of the simulation")
    

class ListSimulationAccounts(Page):
    simulation_id: str = Field(..., description="The id of the simulation")
