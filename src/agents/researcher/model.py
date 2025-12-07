import operator
from typing import Annotated, List, TypedDict
from pydantic import BaseModel, Field
from langgraph.graph import MessagesState

class Analyst(BaseModel):
    affiliation: str = Field(description='Primary affiliation of the analyst')
    name: str = Field('Name of the analyst')
    role: str = Field('Role of the analyst in the context of the topic')
    description: str = Field('Description of the analyst focus, concerns and motives')

    @property
    def persona(self) -> str:
        return f"Name: {self.name}\nRole: {self.role}\nAffiliation: {self.affiliation}\nDescription: {self.description}"
    

class Perspectives(BaseModel):
    analysts: list[Analyst] = Field(description='List of analysts with their details')


class AnalystReview(BaseModel):
    """Review on generated analysts"""
    approved: str = Field(description='The approval status of the generated analyst personas; If approved then YES else NO')
    feedback: str = Field(description='The review on the generated analyst personas')


class AnalystState(TypedDict):
    analysts: list[Analyst]
    depth: str
    topic: str
    num_analysts: int
    feedback: str
    approved: bool
    iteration: int
    max_turns: int


class InterviewerState(MessagesState):
    topic: str
    analyst: Analyst
    context: Annotated[list, operator.add]
    max_turns: int


class Search(BaseModel):
    """Search for retrieval"""
    query: str = Field(description="The query for retrival")

class ResearchState(TypedDict):
    num_analysts: int
    depth: str
    max_analyst_turns: int
    max_interview_turns: int
    analysts: List[Analyst]
    documents: Annotated[list, operator.add]
    topic: str