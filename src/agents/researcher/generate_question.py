from langchain_core.messages import SystemMessage, HumanMessage

from src.agents.researcher.model import InterviewerState
from src.config.llms import get_llm


question_prompt = """
    You are an interviewer with the role: {role}.  
    Your task is to conduct an in-depth interview on the topic: {topic}.  

    Context:  
    You have access to the following previously asked questions and answers:  
    {context}  

    Guidelines:  
    1. Use the context of prior Q&A to avoid repeating questions.  
    2. If an answer is vague, incomplete, or unclear, ask a direct follow-up question for clarification.  
    3. Focus on vital, probing questions that uncover deeper insights about the topic.  
    4. Ensure the flow of questions feels natural and builds logically on previous answers.  
    5. Always phrase questions clearly and professionally.  

    Output:  
    Return only the next best interview question (or "" if none remain).
"""

def generate_question(state: InterviewerState):
    analyst = state['analyst']
    context = state['context']
    topic = state['topic']

    formatted_context = "\n\n".join(str(item) for item in context)

    system_message = question_prompt.format(role=analyst['role'], context=formatted_context, topic=topic, name=analyst['name'])

    llm = get_llm()
    response = llm.invoke([SystemMessage(content=system_message)] + [HumanMessage(content=f"Ask the next question")])
    return {'messages': [HumanMessage(content=response.content, name=analyst['name'])]}

GENERATE_QUESTION = 'generate_question'