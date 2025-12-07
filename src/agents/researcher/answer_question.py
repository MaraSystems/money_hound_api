from langchain_core.messages import SystemMessage, HumanMessage

from src.agents.researcher.model import InterviewerState
from src.config.llms import llm


answer_prompt = """
    You are an expert analyst.  
    Your task is to answer a user’s question on given topic using the provided context.  

    Question: {question}  
    Context: {context}  
    Topic: {topic}

    Guidelines:  
    1. Use ONLY the information from the context. Do not make up facts.  
    2. Combine and synthesize relevant points instead of copying text directly.  
    3. If information is unclear or incomplete, acknowledge the gap.  
    4. Keep the answer concise, structured, and directly relevant.  
    5. Where multiple perspectives exist, explain them clearly.   
    6. Always reference sources inline with numbers like [1], [2], [3].  

    Output format:  
    - **Answer:** A well-structured, clear response (1–3 short paragraphs).  
    - **Sources:** A numbered list of the sources actually used.  
"""

def generate_answer(state: InterviewerState):
    messages = state['messages']
    last_question = messages[-1]
    context = state['context']
    topic = state['topic']

    formatted_context = "\n\n".join(str(item) for item in context)
    system_message = answer_prompt.format(question=last_question, context=formatted_context, topic=topic)
    response = llm.invoke([SystemMessage(content=system_message)] + [HumanMessage(content=f"Answer the question")])
    return {'messages': [HumanMessage(content=response.content, name='Expert')]}

GENERATE_ANSWER = 'generate_answer'