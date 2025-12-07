from datetime import datetime
from typing import List
from pydantic import BaseModel, Field, computed_field

from src.lib.utils.base_entity import BaseEntity
from src.lib.utils.pagination import Page


class CreateSimulationAccount(BaseModel):
    account_no: str = Field(..., description="The account no of the account")
    account_name: str = Field(..., description="The account name of the account")
    bank_name: str = Field(..., description="The bank_name of the account")
    balance: float = Field(..., description="The balance of the account")
    kyc: int = Field(..., description="The kyc no of the account")
    bvn: str = Field(..., description="The bvn no of the account")
    merchant: bool = Field(..., description="The merchant status of the account")
    opening_device: str = Field(..., description="The device the account was opened with")
    simulation_id: str = Field(..., description="The id of the simulation")


    @computed_field
    @property
    def created_at(self) -> datetime:
        return datetime.now()
    
    @computed_field
    @property
    def updated_at(self) -> datetime:
        return datetime.now()


class SimulationAccount(BaseEntity):
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
