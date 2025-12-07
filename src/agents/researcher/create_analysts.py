from src.agents.analysts.analyst_graph import get_analyst_graph
from src.agents.researcher.model import ResearchState

analyst_graph = get_analyst_graph()

def create_analysts(state: ResearchState):
    topic = state['topic']
    depth = state['depth']

    num_analysts = state.get('num_analysts', 2)
    max_analyst_turns = state.get('max_analyst_turns', 2)
    response = analyst_graph.invoke({'topic': topic, 'num_analysts': num_analysts, 'max_turns': max_analyst_turns, 'depth': depth})

    return {'analysts': response['analysts']}

CREATE_ANALYSTS = 'create_analysts'