from datetime import datetime
from typing import Literal, Optional
from pydantic import BaseModel, Field, computed_field

from src.lib.utils.base_entity import BaseEntity
from src.lib.utils.pagination import Page


TransactionCategory = Literal['OPENING', 'WITHDRAWAL', 'DEPOSIT', 'REVERSAL', 'PAYMENT', 'BILL', 'TRANSFER', 'LOAN']


class InitiateSimulationTransaction(BaseModel):
    amount: float = Field(..., description="The amount of the transaction")
    holder: str = Field(..., description="The account that initiated the transaction")
    holder_bank: str = Field(..., description="The bank of the transaction initiator"),
    related: str = Field(..., description="The other account related to the transaction")
    related_bank: str = Field(..., description="The bank of the transaction's other party")
    latitude: float = Field(..., description="The latitude of the transaction location")
    longitude: float = Field(..., description="The longitude of the transaction location")
    type: Literal['DEBIT', 'CREDIT'] = Field(..., description="The type of transaction")
    category: TransactionCategory = Field(..., description="The category of the transaction")
    channel: Literal['APP', 'CARD', 'USSD'] = Field(..., description="The channel used for the transaction")
    device: str = Field(..., description="The device used for the transaction")
    simulation_id: str = Field(..., description="The id of the simulation")

    @computed_field
    @property
    def time(self) -> datetime:
        return datetime.now()


class CreateSimulationTransaction(InitiateSimulationTransaction):
    balance: float = Field(..., description="The balance of the transaction")
    status: Literal['FAILED', 'SUCCESS'] = Field(..., description="The status of the transaction")
    reference: str = Field(..., description="The reference of the transaction")
    reported: bool = Field(..., description="The report status of the transaction")

    @computed_field
    @property
    def created_at(self) -> datetime:
        return datetime.now()
    
    @computed_field
    @property
    def updated_at(self) -> datetime:
        return datetime.now()


class SimulationTransaction(BaseEntity):
    amount: float = Field(..., description="The amount of the transaction")
    balance: float = Field(..., description="The balance of the transaction")
    time: datetime = Field(..., description="The time of the transaction")
    holder: str = Field(..., description="The account that initiated the transaction")
    holder_bank: str = Field(..., description="The bank of the transaction initiator"),
    related: str = Field(..., description="The other account related to the transaction")
    related_bank: str = Field(..., description="The bank of the transaction's other party")
    latitude: float = Field(..., description="The latitude of the transaction location")
    longitude: float = Field(..., description="The longitude of the transaction location")
    status: Literal['FAILED', 'SUCCESS'] = Field(..., description="The status of the transaction")
    type: Literal['DEBIT', 'CREDIT'] = Field(..., description="The type of transaction")
    category: TransactionCategory = Field(..., description="The category of the transaction")
    channel: Literal['APP', 'CARD', 'USSD'] = Field(..., description="The channel used for the transaction")
    device: str = Field(..., description="The device used for the transaction")
    reference: str = Field(..., description="The reference of the transaction")
    reported: bool = Field(..., description="The report status of the transaction")
    simulation_id: str = Field(..., description="The id of the simulation")


class AnalyzedSimulationTransaction(SimulationTransaction):
    features: dict = Field({}, description="The engineered features of the transaction")
    

class ListSimulationTransactions(Page):
    simulation_id: str = Field(..., description="The id of the simulation")
    status: Optional[Literal['FAILED', 'SUCCESS']] = Field(None, description="The status of the transaction")
    type: Optional[Literal['DEBIT', 'CREDIT']] = Field(None, description="The type of transaction")
    category: Optional[TransactionCategory] = Field(None, description="The category of the transaction")
    channel: Optional[Literal['APP', 'CARD', 'USSD']] = Field(None, description="The channel used for the transaction")
    reported: Optional[bool] = Field(None, description="The report status of the transaction")
    

class TransactionsAnalysis(BaseModel):
    numerical: dict = Field(..., description="The numerical description of the transacions")
    categorical: dict = Field(..., description="The categorical description of the transacions")
    volumns: dict = Field(..., description="The volumn description of the transacions")
    proportions: dict = Field(..., description="The proportional description of the transacions")
