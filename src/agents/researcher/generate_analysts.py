from src.agents.researcher.model import AnalystState, Perspectives
from langchain_core.messages import SystemMessage, HumanMessage

from src.config.llms import llm

analyst_instructions = """
    You are tasked with creating a set of AI analysts personas. Follow these instructions carefully:

    1. First review the research topic: {topic}
    2. Examine the editorial feedback that has been optionally provided to guide the creation of the analysts: {feedback}
    3. Determin the most interesting themes based upon the documents and/or feedback above
    4. Pick the top {max_analysts} themes
    5. Assign one analyst to each theme.
"""

def generate_analysts(state: AnalystState):
    topic = state['topic']
    max_analysts = state.get('max_analyst', 3)
    feedback = state.get('feedback', '')
    iteration = state.get('iteration', 0)

    structured_llm = llm.with_structured_output(Perspectives)
    system_message = analyst_instructions.format(topic=topic, max_analysts=max_analysts, feedback=feedback)
    response = structured_llm.invoke([SystemMessage(content=system_message)] + [HumanMessage(content='Generate the set of analysts.')])

    analysts = map(lambda a: a.model_dump(), response.analysts)
    return {'analysts': list(analysts), 'iteration': iteration + 1}

GENERATE_ANALYSTS = 'generate_analysts'