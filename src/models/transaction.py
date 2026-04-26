from datetime import datetime
from decimal import Decimal
from typing_extensions import Literal, Optional
from pydantic import BaseModel, Field, computed_field

from src.models.location import SimulationLocation
from src.models.pagination import Page
from src.models.entity import Creator, Entity


TransactionCategory = Literal['CASH_IN', 'CASH_OUT', 'ADJUSTMENT', 'FEE', 'TRANSFER']
TransactionPurpose = Literal["OPENING", "PAYMENT", "BILL", "LOAN_DISBURSEMENT", "LOAN_REPAYMENT", "SALARY"]
TransactionChannel = Literal['APP', 'CARD', 'USSD']
TransactionStatus = Literal['FAILED', 'SUCCESS', 'PENDING', 'REVERSED']

class Transaction(Entity):
    amount: Decimal = Field(..., description="The amount of the transaction")
    time: datetime = Field(..., description="The time of the transaction")
    from_account: str = Field(..., description="The account that initiated the transaction")
    to_account: str = Field(..., description="The other account related to the transaction")
    location: SimulationLocation = Field(..., description="The location of the transaction location")
    status: TransactionStatus = Field(..., description="The status of the transaction")
    category: TransactionCategory = Field(..., description="The category of the transaction")
    purpose: TransactionPurpose = Field(..., description="The purpose of the transaction")
    channel: TransactionChannel = Field(..., description="The channel used for the transaction")
    reported: bool = Field(..., description="The report status of the transaction")
    reversed_id: Optional[str] = Field(..., description="The id of the reversed transaction")
    device_id: str = Field(..., description="The device used for the transaction")
    reference_id: str = Field(..., description="The reference of the transaction")
    simulation_id: str = Field(..., description="The id of the simulation")


class InitiateTransaction(BaseModel):
    amount: Decimal = Field(..., description="The amount of the transaction")
    from_account: str = Field(..., description="The account that initiated the transaction")
    to_account: str = Field(..., description="The other account related to the transaction")
    location: SimulationLocation = Field(..., description="The location of the transaction location")
    category: TransactionCategory = Field(..., description="The category of the transaction")
    purpose: TransactionPurpose = Field(..., description="The purpose of the transaction")
    channel: TransactionChannel = Field(..., description="The channel used for the transaction")
    device_id: str = Field(..., description="The device used for the transaction")
    simulation_id: str = Field(..., description="The id of the simulation")

    @computed_field
    @property
    def time(self) -> datetime:
        return datetime.now()


class CreateTransaction(InitiateTransaction, Creator):
    status: TransactionStatus = Field(..., description="The status of the transaction")
    reference_id: str = Field(..., description="The reference of the transaction")
    reported: bool = Field(..., description="The report status of the transaction")


class AnalyzedTransaction(Transaction):
    features: dict = Field({}, description="The engineered features of the transaction")
    

class ListTransactions(Page):
    simulation_id: str = Field(..., description="The id of the simulation")
    status: Optional[TransactionStatus] = Field(None, description="The status of the transaction")
    category: Optional[TransactionCategory] = Field(None, description="The category of the transaction")
    channel: Optional[TransactionChannel] = Field(None, description="The channel used for the transaction")
    reported: Optional[bool] = Field(None, description="The report status of the transaction")
    

class TransactionsAnalysis(BaseModel):
    numerical: dict = Field(..., description="The numerical description of the transacions")
    categorical: dict = Field(..., description="The categorical description of the transacions")
    volumns: dict = Field(..., description="The volumn description of the transacions")
    proportions: dict = Field(..., description="The proportional description of the transacions")
