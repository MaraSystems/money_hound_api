from langchain_core.documents import Document

from src.agents.researcher.model import ResearchState
from src.agents.interviewers.interviewer_graph import get_interviewer_graph

interview_graph = get_interviewer_graph()

def conduct_interviews(state: ResearchState):
    analysts = state['analysts']
    topic = state['topic']
    max_interview_turns = state.get('max_interview_turns', 2)

    for analyst in analysts:
        response = interview_graph.invoke({'topic': topic, 'analyst': analyst, 'max_turns': max_interview_turns})
        context = response['context']

        documents = [
            Document(page_content=item['content'], metadata={'title': item['title'], 'url': item['url']}) 
            for item in context
        ]

        state['documents'].extend(documents)
        
    return state

CONDUCT_INTERVIEWS = 'conduct_interviews'