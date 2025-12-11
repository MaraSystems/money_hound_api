from typing import TypedDict
from langchain_core.messages import SystemMessage
from langgraph.graph import StateGraph
from langchain_core.tools import tool

from src.config.llms import get_llm

class SupportState(TypedDict):
    query: str
    reasoning: str
    reply: str


WORKFLOW_PROMPT = """
    You are the Support Agent for TaxQ, you handle small talk, inquiries, troubleshooting, and general support.
    Your responsibilities include welcoming users warmly, understanding their intent, providing clear and straightforward answers, and guiding them through platform features.

    You always receive two inputs:
    1.  The user's actual query: {query}
    2.  An optional reason {reasoning} explaining why the query may be out of context for the system.
    
    Your job is to interpret both pieces of information and produce the most helpful response possible.
    If the query is valid and within context, answer it clearly, directly, and helpfully.
    If the query is out of context and can not be classified as one of the following (small talk, inquiries, troubleshooting, and general support), then use the provided reason to guide your response—redirect the user, clarify the limitation, or help them reformulate their request.

    Maintain a calm, supportive tone.
    Acknowledge the user’s intent, address confusion when it appears, and always offer a path forward, even when the system cannot fulfill the request as written.

    Your goal: ensure the user feels understood, helped, and guided, regardless of whether the query fits the system’s expected domain.
"""


def support_model(state: SupportState):
    query = state['query']
    reasoning = state['reasoning']

    formatted_prompt = WORKFLOW_PROMPT.format(query=query, reasoning=reasoning)
    system_message = SystemMessage(content=formatted_prompt)

    llm = get_llm()
    response = llm.invoke([system_message]+[SystemMessage(content='Answer the user')])
    state['reply'] = response.content
    return state


SUPPORT_MODEL = 'support_model'

support_builder = StateGraph(SupportState)

support_builder.add_node(SUPPORT_MODEL, support_model)
support_builder.set_entry_point(SUPPORT_MODEL)
support_builder.set_finish_point(SUPPORT_MODEL)

def get_support_graph():
    return support_builder.compile()


@tool
def support_tool(query: str, reasoning=None):
    """Tool to provide customer support to users"""
    graph = get_support_graph()
    return graph.invoke({'query': query, 'reasoning': reasoning})