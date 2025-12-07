from langgraph.graph import StateGraph, END

from src.agents.researcher.model import InterviewerState

from .generate_question import GENERATE_QUESTION, generate_question
from .search_web import WEB_SEARCH, web_search
from .answer_question import GENERATE_ANSWER, generate_answer

interviewer_builder = StateGraph(InterviewerState)

interviewer_builder.add_node(GENERATE_QUESTION, generate_question)
interviewer_builder.add_node(WEB_SEARCH, web_search)
interviewer_builder.add_node(GENERATE_ANSWER, generate_answer)

interviewer_builder.set_entry_point(GENERATE_QUESTION)
interviewer_builder.add_edge(GENERATE_QUESTION, WEB_SEARCH)
interviewer_builder.add_edge(WEB_SEARCH, GENERATE_ANSWER)
interviewer_builder.set_finish_point(GENERATE_ANSWER)

def get_interviewer_graph():
    return interviewer_builder.compile()