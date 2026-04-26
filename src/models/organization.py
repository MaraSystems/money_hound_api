from datetime import datetime
from typing_extensions import Literal
from pydantic import BaseModel, Field, field_validator

from src.models.location import Location
from src.models.entity import Creator, Entity
from src.models.pagination import Page

OrganizationExpenseCategory = Literal['FOOD', 'TRANSPORT', 'HOUSING', 'UTILITIES', 'CLOTHING', 'HEALTH', 'EDUCATION', 'ENTERTAINMENT', 'OTHER']
OrganizationIncomeCategory = Literal['SALARY', 'CONTRACT', 'BUSINESS', 'INVESTMENT', 'OTHER']
OrganizationStatus = Literal['ACTIVE', 'INACTIVE', 'SUSPENDED', 'CLOSED']   
OrganizationIndustry = Literal['FINANCE', 'TECHNOLOGY', 'HEALTHCARE', 'ENERGY', 'CONSTRUCTION', 'MANUFACTURING', 'RETAIL', 'EDUCATION', 'GOVERNMENT', 'OTHER']
OrganizationType = Literal['CORPORATION', 'PARTNERSHIP', 'LLC', 'SOLE_PROPRIETORSHIP', 'OTHER']

class OrganizationIdentity(BaseModel):
    CAC_REGISTRATION_NUMBER: str = Field(
        ...,
        description="CAC Registration Number — Corporate Affairs Commission"
    )
    TAX_IDENTIFICATION_NUMBER: str = Field(
        ...,
        description="Tax Identification Number — FIRS issued"
    )
    VAT_NUMBER: str = Field(
        default=None,
        description="VAT registration number — required if turnover exceeds ₦25M/year"
    )
    BUSINESS_PERMIT: str = Field(
        default=None,
        description="Business operating permit number — state or federal"
    )
    CENTRAL_BANK_OF_NIGERIA_LICENSE: str = Field(
        default=None,
        description="Central Bank of Nigeria license number — fintechs, banks, PSPs"
      )
    SECURITIES_AND_EXCHANGE_COMMISSION_REGISTRATION: str = Field(
        default=None,
        description="Securities and Exchange Commission registration — investment firms"
    )
    SPECIAL_CONTROL_UNIT_AGAINST_MONEY_LAUNDERING_CERTIFICATE: str = Field(
        default=None,
        description="Special Control Unit Against Money Laundering certificate — required for DNFIs"
    )
    

class OrganizationExpense(BaseModel):
    frequency: float = Field(..., description="How often organization spends", gt=0, lt=1)
    income_ratio: float = Field(..., description="Fraction income organization spends", gt=0, lt=1)
    power: float = Field(..., description="How much the person should be spending", gt=0)
    variability: float = Field(..., description="Variation on how much the person should be spending", gt=0)
    preferences: dict[OrganizationExpenseCategory, float] = Field(default_factory=lambda: {}, description="Organization expense category weights, sums to 1")

    @field_validator('preferences')
    @classmethod
    def validate_preferences(cls, value: dict[OrganizationExpenseCategory, float]) -> dict[OrganizationExpenseCategory, float]:
        if sum(value.values()) != 1:
            raise ValueError("OrganizationExpense Preferences must sum to 1")
        return value


class OrganizationIncome(BaseModel):
    streams: dict[OrganizationIncomeCategory, float] = Field(default_factory=lambda: {}, description="Organization income streams, sums to 1")
    power: float = Field(..., description="How much the person should be making", gt=0)
    variability: float = Field(..., description="Variation on how much the person should be making", gt=0)
    stability: float = Field(..., description="how stable is the organization with making money", gt=0, lt=1)
    trend: float = Field(..., description="how is the organization making money, positive or negative", gt=-1, lt=1)

    @field_validator('streams')
    @classmethod
    def validate_streams(cls, value: dict[OrganizationIncomeCategory, float]) -> dict[OrganizationIncomeCategory, float]:
        if sum(value.values()) != 1:
            raise ValueError("OrganizationIncome Streams must sum to 1")
        return value


class OrganizationCredit(BaseModel):
    payback: float = Field(..., description="The frequency the organization should be paying back", gt=0, lt=1)
    borrow: float = Field(..., description="The frequency the organization should be borrowing", gt=0, lt=1)


class OrganizationRisk(BaseModel):
    tolerance: float = Field(..., description="The tolerance of the organization to risk", gt=0, lt=1)
    loss_aversion: float = Field(..., description="The frequency the organization should be loss averse", gt=0, lt=1)


class OrganizationFraud(BaseModel):
    identity_theft: float = Field(..., description="The frequency the organization should be committing identity fraud", gt=0, lt=1)
    structural_fraud: float = Field(..., description="The frequency the organization should be committing structural fraud", gt=0, lt=1)
    account_takeover: float = Field(..., description="The frequency the organization should be committing account takeover", gt=0, lt=1)
    chargeback: float = Field(..., description="The frequency the organization should be committing chargeback", gt=0, lt=1)
    smurfing: float = Field(..., description="The frequency the organization should be committing smurfing", gt=0, lt=1)


class OrganizationBranch(BaseModel):
    branch_id: str = Field(..., description="Unique identifier for the branch")
    name: str = Field(..., description="Branch name e.g. 'Lagos Island Branch'")
    location: Location = Field(..., description="Physical location of the branch")
    status: OrganizationStatus = Field(..., description="Operational status of this branch")
    opened_at: datetime = Field(..., description="When this branch opened")
    is_headquarters: bool = Field(default=False, description="Whether this is the HQ")


class Organization(Entity):
    name: str = Field(..., description="The name of the organization")
    email: str = Field(..., description="The email of the organization")
    location: Location = Field(..., description="The location of the organization")
    industry: OrganizationIndustry = Field(..., description="The industry of the organization")
    size: int = Field(..., description="The size of the organization")
    type: OrganizationType = Field(..., description="The type of the organization")
    founded_at: datetime = Field(..., description="The date the organization was founded")
    status: OrganizationStatus = Field(..., description="The status of the organization")
    ownership: dict[str, float] = Field(..., description="The ownership structure of the organization")
    simulation_id: str = Field(..., description="The id of the simulation")

    @property
    def headquarters(self) -> OrganizationBranch:
        return next((branch for branch in self.branches if branch.is_headquarters), None)

    @property
    def all_locations(self) -> list[Location]:
        return [self.location] + [branch.location for branch in self.branches]

    @property
    def active_branches(self) -> list[OrganizationBranch]:
        return [branch for branch in self.branches if branch.status == 'ACTIVE']


class CreateOrganization(Creator):
    name: str = Field(..., description="The name of the organization")
    email: str = Field(..., description="The email of the organization")
    location: Location = Field(..., description="The location of the organization")
    industry: OrganizationIndustry = Field(..., description="The industry of the organization")
    size: int = Field(..., description="The size of the organization")
    type: OrganizationType = Field(..., description="The type of the organization")
    expense: OrganizationExpense = Field(..., description="The expense profile of the organization")
    income: OrganizationIncome = Field(..., description="The income profile of the organization")
    credit: OrganizationCredit = Field(..., description="The credit profile of the organization")
    risk: OrganizationRisk = Field(..., description="The risk profile of the organization")
    fraud: OrganizationFraud = Field(..., description="The fraud profile of the organization")
    founded_at: datetime = Field(..., description="The date the organization was founded")
    status: OrganizationStatus = Field(..., description="The status of the organization")
    simulation_id: str = Field(..., description="The id of the simulation")
    branches: list[OrganizationBranch] = Field(default_factory=list, description="The branches of the organization")

    @field_validator('branches')
    @classmethod
    def validate_branches(cls, value: list[OrganizationBranch]) -> list[OrganizationBranch]:
        if len(value) == 0:
            raise ValueError("Organization must have at least one branch")
        return value


class ListOrganizations(Page):
    simulation_id: str = Field(..., description="The id of the simulation")
