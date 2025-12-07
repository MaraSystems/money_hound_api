from langchain_core.messages import AIMessage, HumanMessage
from langgraph.graph.state import CompiledStateGraph
import json

from src.domains.simulations.model import PredictTransaction
from src.lib.utils.response import DataResponse


async def predict(payload: PredictTransaction):
    ...