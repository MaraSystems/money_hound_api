from langchain_tavily import TavilySearch
from langchain_core.messages import SystemMessage, HumanMessage

from src.agents.researcher.model import InterviewerState
from src.config.llms import llm

tavily_search = TavilySearch(max_results=3, search_depth='advanced')

query_prompt = """
You are a search optimization assistant.  
Your task is to take an interview question and rewrite it into the most effective, concise web search query.  

Guidelines:  
1. Keep the core intent of the question intact.  
2. Remove unnecessary filler words like "can you tell me" or "how do you think".  
3. Use keywords and phrases that would retrieve the most relevant search results.  
4. If the question is vague, infer the most likely specific search intent.  
5. Ensure the query is clear, precise, and ready for a search engine.  

Example:  
Question: "How do businesses in Nigeria adapt to the new VAT reform?"  
Query: "Nigeria VAT reform 2024 business adaptation strategies"  

Now convert this question into a web search query:  
Question: {question}  
Output: <search query>
"""

def web_search(state: InterviewerState):
    messages = state['messages']
    last_question = messages[-1]

    system_message = query_prompt.format(question=last_question)
    response = llm.invoke([SystemMessage(content=system_message)] + [HumanMessage(content=f"Turn the question into a search query")])

    search_result = tavily_search.invoke(response.content)
    formatted_search_result = [{'url': result['url'], 'title': result['title'], 'content': result['content']} for result in search_result['results']]
    
    return {'context': formatted_search_result}

WEB_SEARCH = 'web_search'
    