from langchain_core.messages import SystemMessage, HumanMessage
from langgraph.graph import StateGraph, MessagesState
from typing_extensions import TypedDict, Generic, TypeVar
from pydantic import BaseModel, Field, Gene

T = TypeVar("T")

from src.config.llms import llm

class Evaluation(BaseModel):
    """Evaluation on an answer to a query"""
    valid: str = Field(description='Did the query was answered correctly')
    review: str = Field(description='Critique of the answer based on the query')


class ReflectState(TypedDict, Generic[T]):
    query: str
    answer: T
    reflection: Evaluation


def reflection(prompt: str):
    def generate_node(state: ReflectState[t]):
        ...


    def reflect_node(state: ReflectState):
        ...