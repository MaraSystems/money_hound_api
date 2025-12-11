from typing import List, TypedDict, Literal
from langchain_core.messages import SystemMessage, HumanMessage
from pydantic import BaseModel, Field
from langgraph.graph import StateGraph

from src.lib.utils.function import Function, FunctionEnum
from src.config.llms import get_llm


class Step(BaseModel):
    """
    Represents a procedural step required to respond to a user's query.
    Each step defines what needs to be done, why it’s needed, and which tool should handle it.
    """

    workload: str = Field(
        None,
        description="Description of the workload to be executed.",
        examples=[
            "Extract key tax information",
            "Perform compliance validation"
        ]
    )

    function: FunctionEnum = Field(
        None,
        description="Name of the function to be used for executing this step."
    )


class BreakDown(BaseModel):
    """
    Represents all the steps to be executed in order to fully respond to the user's query
    """
    workflow: List[Step] = Field(
        ...,
        description="Ordered list of steps required to fully respond to the user's query."
    )

    reasoning: str = Field(
        None,
        description="A concise summary of the workflow's overall purpose or target outcome.",
        examples=["Ensure user's tax filing query is processed through extraction, validation, and compliance review."]
    )


class WorkflowState(TypedDict):
    query: str
    functions: List[Function]
    reasoning: str
    workflow: List[Step]


WORKFLOW_PROMPT = """
    You are the Planner Agent for TaxQ — an intelligent system that manages tax, finance, and business queries by coordinating specialized functions.

    You have access only to the following functions:
    {functions}

    Your role is to break down the user’s query into a valid, executable workflow using only the listed functions.
    Each function represents a specialized capability within the TaxQ system.
    
    The abilities of each function is in the use_case, use that to access what the function can do.
    If a required step cannot be completed with the available functions, 
        - Then you must reply to the user that you are not allowed to answer the query.
    ---

    ### TASK
    1. Analyze the user’s query to determine what needs to be done to fully and accurately address it.
    2. Decompose the process into a sequence of ordered, minimal, and logically structured steps.
    3. Each step must include:
        - workload: a short, descriptive action.
        - function: one of the listed functions only.
    4. Do not include commentary, or explanation outside the JSON structure.
    ---

    Rules:
    If the workflow can be built, include the relevant steps and provide a user-friendly explanation in the reasoning field describing why those steps and functions were selected.

    If the workflow cannot be built, set "workflow": [] and explain that it is out of scope.
    Else return the workflows and reasoning that will guide an LLM carry out the corresponding workflow with respect to the query.
    ---
    
    ### OUTPUT FORMAT
    Respond **only** in valid JSON matching this schema:
        - workflow:
            - workload: "string",
            - function: "string" (The name of the function)

        - reasoning: "string" (Message to the user, must be user friendly)
    ---

    User Query:
    {query}

    Now, produce the structured breakdown as valid JSON.
"""


def workflow_model(state: WorkflowState):
    query = state['query']
    functions = state['functions']

    formatted_prompt = WORKFLOW_PROMPT.format(query=query, functions=functions)
    system_message = SystemMessage(content=formatted_prompt)

    llm = get_llm()
    response = llm.with_structured_output(BreakDown).invoke([system_message]+[HumanMessage(content='Is the query within scope?')])
    state['workflow'] = response.workflow
    state['reasoning'] = response.reasoning
    return state


WORKFLOW_MODEL = 'workflow_model'

workflow_builder = StateGraph(WorkflowState)

workflow_builder.add_node(WORKFLOW_MODEL, workflow_model)
workflow_builder.set_entry_point(WORKFLOW_MODEL)
workflow_builder.set_finish_point(WORKFLOW_MODEL)

def get_workflow_graph():
    return workflow_builder.compile()