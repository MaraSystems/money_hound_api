from langgraph.graph import StateGraph, END, MessagesState
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_core.tools import tool
from typing import TypedDict, Annotated, List
from langgraph.prebuilt import ToolNode, tools_condition
from src.graphs.support import get_support_graph
from src.graphs.workflow import Step, get_workflow_graph
from src.graphs.enhancer import get_enhancer_graph

from src.config.llms import llm
from src.lib.utils.function import TAXQ_TOOLS, FunctionEnum, Function, TAXQ_FUNCTIONS


class TaxqState(MessagesState):
    workflow: List[Step]
    functions: List[Function]


all_tools = TAXQ_TOOLS.values()
tool_model = ToolNode(tools=all_tools)
TOOL_MODEL = 'tools'


ENHANCE_NODE = 'enhance_node'
def enhance_node(state: TaxqState):
    graph = get_enhancer_graph()
    query = state['messages'][-1]
    context = state.get('context', ''),
    feedback = state.get('feedback', '')

    response = graph.invoke({'query': query, 'context': context, 'feedback': feedback})
    return {'messages': [AIMessage(content=response['enhanced'], name=ENHANCE_NODE)]}


WORKFLOW_NODE = 'workflow_node'
def workflow_node(state: TaxqState):
    graph = get_workflow_graph()
    query = state['messages'][-1]
    functions = state['functions']

    response = graph.invoke({'query': query, 'functions': functions})
    return {'messages': [AIMessage(content=response['reasoning'], name=WORKFLOW_NODE)], 'workflow': response['workflow']}


SUPPORT_NODE = 'support_node'
def support_node(state: TaxqState):
    graph = get_support_graph()
    human_massages = list(filter(lambda message: isinstance(message, HumanMessage), state['messages']))
    query = human_massages[-1]
    reasoning = state['messages'][-1]

    response = graph.invoke({'query': query, 'reasoning': reasoning})
    return {'messages': [AIMessage(content=response['reply'], name=SUPPORT_NODE)]}


EXECUTE_MODEL = 'execute_model'
def execute_model(state: TaxqState):
    workflow = state['workflow']

    tool_choice = [step.function for step in workflow]
    tools = [TAXQ_TOOLS[function] for function in tool_choice]
    
    llm_with_tools = llm.bind_tools(tools=tools, tool_choice=tool_choice)
    response = llm_with_tools.invoke(state['messages'])

    return {'messages': [response]}


def should_execute(state: TaxqState):
    workflow = state['workflow']
    return EXECUTE_MODEL if len(workflow) else SUPPORT_NODE


taxq_builder = StateGraph(TaxqState)

taxq_builder.add_node(ENHANCE_NODE, enhance_node)
taxq_builder.add_node(WORKFLOW_NODE, workflow_node)
taxq_builder.add_node(SUPPORT_NODE, support_node)
taxq_builder.add_node(EXECUTE_MODEL, execute_model)
taxq_builder.add_node(TOOL_MODEL, tool_model)

taxq_builder.set_entry_point(ENHANCE_NODE)
taxq_builder.add_edge(ENHANCE_NODE, WORKFLOW_NODE)
taxq_builder.add_conditional_edges(WORKFLOW_NODE, should_execute, [EXECUTE_MODEL, SUPPORT_NODE])
taxq_builder.add_conditional_edges(EXECUTE_MODEL, tools_condition, [TOOL_MODEL, END])
taxq_builder.add_edge(TOOL_MODEL, EXECUTE_MODEL)
taxq_builder.add_edge(SUPPORT_NODE, END)


def get_taxq_graph():
    return taxq_builder.compile()