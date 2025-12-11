from langgraph.graph import StateGraph
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.tools import tool
from typing import TypedDict

from src.config.llms import get_llm

class EnhanceState(TypedDict):
    query: str
    enhanced: str
    context: str
    feedback: str


ENHANCE_PROMPT = """
    You are the Query Enhancer.

    Your goal is to improve the user's query by making it clearer, more specific, and self-contained, while keeping the original intent unchanged.

    You may be given additional context or feedback, but they are optional.
    If provided, use them to make the enhancement more accurate.

    ---

    Optional Context:
    {context}

    Optional Feedback:
    {feedback}

    User Query:
    {query}

    ---

    Respond only the enhanced query
"""


def enhance_model(state: EnhanceState):
    query = state['query']
    context = state.get('context', '')
    feedback = state.get('feedback', '')
    
    formatted_prompt = ENHANCE_PROMPT.format(context=context, feedback=feedback, query=query)
    system_message = SystemMessage(content=formatted_prompt)
    llm = get_llm()
    response = llm.invoke([system_message]+[HumanMessage(content='Enhance the query')])

    return {'enhanced': response.content}

ENHANCE_MODEL = 'enhance_model'

enhance_builder = StateGraph(EnhanceState)

enhance_builder.add_node(ENHANCE_MODEL, enhance_model)
enhance_builder.set_entry_point(ENHANCE_MODEL)
enhance_builder.set_finish_point(ENHANCE_MODEL)

def get_enhancer_graph():
    return enhance_builder.compile()


@tool
def enhancer_tool(query: str):
    """Tool for enhancing query for better understanding"""

    graph = get_enhancer_graph()
    return graph.invoke({'query': query})