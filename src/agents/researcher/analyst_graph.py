from langgraph.graph import StateGraph, END

from .generate_analysts import GENERATE_ANALYSTS, generate_analysts
from .review_analysts import REVIEW_ANALYSTS, review_analysts
from .model import AnalystState

def is_approved(state: AnalystState):
    approved = state['approved']
    iteration = state['iteration']
    max_turns = state.get('max_turns', 3)
    
    if approved or iteration == max_turns:
        return END
    return GENERATE_ANALYSTS


analyst_builder = StateGraph(AnalystState)

analyst_builder.add_node(GENERATE_ANALYSTS, generate_analysts)
analyst_builder.add_node(REVIEW_ANALYSTS, review_analysts)

analyst_builder.set_entry_point(GENERATE_ANALYSTS)
analyst_builder.add_edge(GENERATE_ANALYSTS, REVIEW_ANALYSTS)
analyst_builder.add_conditional_edges(REVIEW_ANALYSTS, is_approved, [GENERATE_ANALYSTS, END])

def get_analyst_graph():
    return analyst_builder.compile()