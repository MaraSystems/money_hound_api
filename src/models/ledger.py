from datetime import datetime
from decimal import Decimal
from typing import Literal
from pydantic import Field
from src.models.entity import Creator, Entity
from src.models.pagination import Page

LedgerCategory = Literal["BANK", "WALLET"]


class Ledger(Entity):
    account_no: str = Field(..., description="The account that owns the ledger")
    time: datetime = Field(..., description="The time of the transaction")
    amount: Decimal = Field(..., description="The amount of the transaction")
    category: LedgerCategory = Field(..., description="The category of ledger")
    provider_id: str = Field(..., description="The organization that owns the ledger")
    transaction_id: str = Field(..., description="The reference of the transaction")
    simulation_id: str = Field(..., description="The id of the simulation")


class CreateLedger(Creator):
    account_no: str = Field(..., description="The account that owns the ledger")
    amount: Decimal = Field(..., description="The amount of the transaction")
    category: LedgerCategory = Field(..., description="The category of ledger")
    provider_id: str = Field(..., description="The organization that owns the ledger")
    transaction_id: str = Field(..., description="The reference of the transaction")
    simulation_id: str = Field(..., description="The id of the simulation")


class ListLedger(Page):
    simulation_id: str = Field(..., description="The id of the simulation")
