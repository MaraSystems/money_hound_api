from langgraph.graph import StateGraph

from src.agents.researcher.conduct_interviews import CONDUCT_INTERVIEWS, conduct_interviews
from src.agents.researcher.create_analysts import CREATE_ANALYSTS, create_analysts
from src.agents.researcher.model import ResearchState

research_builder = StateGraph(ResearchState)

research_builder.add_node(CREATE_ANALYSTS, create_analysts)
research_builder.add_node(CONDUCT_INTERVIEWS, conduct_interviews)

research_builder.set_entry_point(CREATE_ANALYSTS)
research_builder.add_edge(CREATE_ANALYSTS, CONDUCT_INTERVIEWS)
research_builder.set_finish_point(CONDUCT_INTERVIEWS)

def get_research_graph():
    return research_builder.compile()