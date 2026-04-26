from typing_extensions import Literal
from uuid import uuid4
from pydantic import  Field, computed_field

from src.models.pagination import Page
from src.models.entity import Creator, Entity

WalletType = Literal["CREDIT", "DEBIT", "CREDIT/DEBIT"]

class CreateWallet(Creator):
    username: str = Field(..., description="The user name of the wallet")
    privider_id: str = Field(..., description="The organization that runs the wallet")
    balance: float = Field(..., description="The balance of the wallet")
    bvn: str = Field(..., description="The bvn no of the wallet")
    opening_device: str = Field(..., description="The device the wallet was opened with")
    simulation_id: str = Field(..., description="The id of the simulation")

    @computed_field
    @property
    def account_number(self) -> str:
        return f"WLT_{self.bank_id[:4]}_{uuid4().hex[:10]}"


class Wallet(Entity):
    wallet_id: str = Field(..., description="The unique identifier of the wallet")    
    username: str = Field(..., description="The user name of the wallet")
    privider_id: str = Field(..., description="The organization that runs the wallet")
    balance: float = Field(..., description="The balance of the wallet")
    bvn: str = Field(..., description="The bvn no of the wallet")
    opening_device: str = Field(..., description="The device the wallet was opened with")
    simulation_id: str = Field(..., description="The id of the simulation")
    

class ListWallets(Page):
    simulation_id: str = Field(..., description="The id of the simulation")
