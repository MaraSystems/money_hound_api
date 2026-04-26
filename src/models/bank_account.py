from decimal import Decimal
from typing_extensions import Literal
from uuid import uuid4
from pydantic import  Field, computed_field

from src.models.pagination import Page
from src.models.entity import Creator, Entity

BankAccountType = Literal["SAVINGS", "CURRENT"]
BankAccountRole = Literal["INDIVIDUAL", "BUSINESS", "AGENT"]
BANKACCOUNTACTION = Literal["HOLD_FUNDS", "ACCEPT_PAYMENTS", "CASH_IN", "CASH_OUT"]

class CreateBankAccount(Creator):
    name: str = Field(..., description="The account name of the account")
    type: BankAccountType = Field(..., description="The type of bank account")
    role: BankAccountRole = Field(..., description="The role of the bank account")
    bank_id: str = Field(..., description="The bank_id of the account")
    balance: Decimal = Field(..., description="The balance of the account")
    kyc_level: int = Field(..., description="The kyc level no of the account")
    bvn: str = Field(..., description="The bvn no of the account")
    opening_device: str = Field(..., description="The device the account was opened with")
    simulation_id: str = Field(..., description="The id of the simulation")

    @computed_field
    @property
    def account_number(self) -> str:
        return f"{self.bank_id[:4]}_{uuid4()}"


class BankAccount(Entity):
    account_no: str = Field(..., description="The account no of the account")
    account_name: str = Field(..., description="The account name of the account")
    account_type: BankAccountType = Field(..., description="The type of bank account")
    role: BankAccountRole = Field(..., description="The role of the bank account")
    bank_id: str = Field(..., description="The bank_id of the account")
    balance: Decimal = Field(..., description="The balance of the account")
    kyc_level: int = Field(..., description="The kyc level no of the account")
    bvn: str = Field(..., description="The bvn no of the account")
    opening_device: str = Field(..., description="The device the account was opened with")
    simulation_id: str = Field(..., description="The id of the simulation")
    

class ListBankAccounts(Page):
    simulation_id: str = Field(..., description="The id of the simulation")


def accountActions(account: BankAccount) -> list[BANKACCOUNTACTION]:
    base: list[BANKACCOUNTACTION] = ['HOLD_FUNDS']

    if account.role == "BUSINESS" or account.role == "AGENT":
        base.append("ACCEPT_PAYMENTS")

    if account.role == "AGENT":
        base.extend(["CASH_IN", "CASH_OUT"])

    return base