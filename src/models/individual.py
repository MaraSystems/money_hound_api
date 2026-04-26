from datetime import datetime
from typing_extensions import Literal
from pydantic import BaseModel, Field, field_validator

from src.models.location import Location
from src.models.pagination import Page
from src.models.entity import Creator, Entity

IndividualExpenseCategory = Literal['FOOD', 'TRANSPORT', 'HOUSING', 'UTILITIES', 'CLOTHING', 'HEALTH', 'EDUCATION', 'ENTERTAINMENT', 'OTHER']
IndividualIncomeCategory = Literal['SALARY', 'CONTRACT', 'BUSINESS', 'INVESTMENT', 'OTHER']
IndividualGender = Literal['MALE', 'FEMALE', 'OTHER']
IndividualStatus = Literal['ACTIVE', 'RETIRED', 'ARRESTED', 'DECEASED']

class IndividualIdentity(BaseModel):
    NATIONAL_IDENTIFICATION_NUMBER: str = Field(..., description="The National Identification Number of the individual")
    PASSPORT_NUMBER: str = Field(..., description="The Passport Number of the individual")
    DRIVER_LICENSE_NUMBER: str = Field(..., description="The Driver License Number of the individual")
    BANK_VERIFICATION_NUMBER: str = Field(..., description="The Bank Verification Number of the individual")
    TAX_IDENTIFICATION_NUMBER: str = Field(..., description="The Tax Identification Number of the individual")


class IndividualExpense(BaseModel):
    frequency: float = Field(..., description="How often individual spends", gt=0, lt=1)
    income_ratio: float = Field(..., description="Fraction income individual spends", gt=0, lt=1)
    power: float = Field(..., description="How much the person should be spending", gt=0)
    variability: float = Field(..., description="Variation on how much the person should be spending", gt=0)
    preferences: dict[IndividualExpenseCategory, float] = Field(default_factory=lambda: {}, description="Individual expense category weights, sums to 1")

    @field_validator('preferences')
    @classmethod
    def validate_preferences(cls, value: dict[IndividualExpenseCategory, float]) -> dict[IndividualExpenseCategory, float]:
        if sum(value.values()) != 1:
            raise ValueError("IndividualExpense Preferences must sum to 1")
        return value


class IndividualIncome(BaseModel):
    streams: dict[IndividualIncomeCategory, float] = Field(default_factory=lambda: {}, description="Individual income streams, sums to 1")
    power: float = Field(..., description="How much the person should be making", gt=0)
    variability: float = Field(..., description="Variation on how much the person should be making", gt=0)
    stability: float = Field(..., description="how stable is the individual with making money", gt=0, lt=1)
    trend: float = Field(..., description="how is the individual making money, positive or negative", gt=-1, lt=1)

    @field_validator('streams')
    @classmethod
    def validate_streams(cls, value: dict[IndividualIncomeCategory, float]) -> dict[IndividualIncomeCategory, float]:
        if sum(value.values()) != 1:
            raise ValueError("IndividualIncome Streams must sum to 1")
        return value


class IndividualCredit(BaseModel):
    payback: float = Field(..., description="The frequency the individual should be paying back", gt=0, lt=1)
    borrow: float = Field(..., description="The frequency the individual should be borrowing", gt=0, lt=1)


class IndividualRisk(BaseModel):
    tolerance: float = Field(..., description="The tolerance of the individual to risk", gt=0, lt=1)
    loss_aversion: float = Field(..., description="The frequency the individual should be loss averse", gt=0, lt=1)


class IndividualFraud(BaseModel):
    identity_theft: float = Field(..., description="The frequency the individual should be committing identity fraud", gt=0, lt=1)
    structural_fraud: float = Field(..., description="The frequency the individual should be committing structural fraud", gt=0, lt=1)
    account_takeover: float = Field(..., description="The frequency the individual should be committing account takeover", gt=0, lt=1)
    chargeback: float = Field(..., description="The frequency the individual should be committing chargeback", gt=0, lt=1)
    smurfing: float = Field(..., description="The frequency the individual should be committing smurfing", gt=0, lt=1)


class CreateIndividual(Creator):
    first_name: str = Field(..., description="The first_name of the individual")
    last_name: str = Field(..., description="The last_name of the individual")
    gender: IndividualGender = Field(..., description="The gender of the individual")
    email: str = Field(..., description="The email of the individual")
    birthdate: datetime = Field(..., description="The date of birth of the individual")
    location: Location = Field(..., description="The location of the individual")
    income: IndividualIncome = Field(...,  description="The income profile of the individual")
    expense: IndividualExpense = Field(...,  description="The expense profile of the individual")
    credit: IndividualCredit = Field(...,  description="The credit profile of the individual")
    risk: IndividualRisk = Field(...,  description="The risk profile of the individual")
    fraud: IndividualFraud = Field(...,  description="The fraud profile of the individual")
    simulation_id: str = Field(..., description="The id of the simulation")


class Individual(Entity):
    first_name: str = Field(..., description="The first_name of the individual")
    last_name: str = Field(..., description="The last_name of the individual")
    gender: IndividualGender = Field(..., description="The gender of the individual")
    email: str = Field(..., description="The email of the individual")
    birthdate: datetime = Field(..., description="The date of birth of the individual")
    location: Location = Field(..., description="The location of the individual")
    income: IndividualIncome = Field(...,  description="The income profile of the individual")
    expense: IndividualExpense = Field(...,  description="The expense profile of the individual")
    credit: IndividualCredit = Field(...,  description="The credit profile of the individual")
    risk: IndividualRisk = Field(...,  description="The risk profile of the individual")
    fraud: IndividualFraud = Field(...,  description="The fraud profile of the individual")
    identity: IndividualIdentity = Field(...,  description="The identity profile of the individual")
    status: IndividualStatus = Field(..., description="The status of the individual")
    simulation_id: str = Field(..., description="The id of the simulation")


class ListIndividuals(Page):
    simulation_id: str = Field(..., description="The id of the simulation")
