from langchain_tavily import TavilySearch
from langgraph.graph import StateGraph, END
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.tools import tool
from typing import TypedDict, Annotated, List
from langchain.schema import Document
from pydantic import BaseModel, Field

from src.config.llms import llm
from src.config.vector_store import get_vector_store


class Rank(BaseModel):
    "Rank documents based on relevance to user query"
    index: int = Field(description='The index of the document in the list of documents')
    relevance: float = Field(description='The relevance of the document with respect to the user query')

class RankList(BaseModel):
    ranks: List[Rank] = Field(description='List of ranks for each document with respect to the user query')

class ResearchState(TypedDict):
    query: str
    documents: List[Document]
    search_count: int


SEARCH_PROMPT = """
    You are a search optimization assistant.  
    Your task is to user's question and rewrite it into the most effective, concise web search_query.  

    Guidelines:  
    1. Keep the core intent of the query intact.  
    2. Remove unnecessary filler words like "can you tell me" or "how do you think".  
    3. Use keywords and phrases that would retrieve the most relevant search results.  
    4. If the question is vague, infer the most likely specific search intent.  
    5. Ensure the query is clear, precise, and ready for a search engine.  

    Example:  
    Query: "How do businesses in Nigeria adapt to the new VAT reform?"  
    Search_Query: "Nigeria VAT reform 2024 business adaptation strategies"  

    Now convert this query into a web search_query:  
    Query: {query}  
    Output: <search_query>
"""

RANKING_PROMPT = """
    You are the Ranking Agent for TaxQ — an intelligent system that retrieves and evaluates documents to determine which are most likely to answer a user’s query.

    Your job is to analyze each document’s relevance and assign a probability score representing the likelihood that it can accurately and completely answer the given query.

    Rank all provided documents according to how useful and informative they are for answering the user’s query.

    You must:
        1. Assess and Analyze each document individually.
        2. Consider content relevance, factual alignment, completeness, and specificity to the query.
        3. Output a probability score between 0 and 1, where:
            1.0 → The document almost certainly answers the query.
            0.5 → The document might partially answer or provide related context.
            0.0 → The document is unrelated or unhelpful.
        4. Do not include commentary or reasoning outside the JSON response.
    
    User Query:
    {query}

    Documents:
    {documents}

    OUTPUT FORMAT
    Respond **only** in valid JSON matching this schema:
        - ranks:
            - index: "number" (The index of the document in the list),
            - relevance: "float" (a float between 0.0 and 1.0, indicating confidence in the document’s ability to answer the query.)
"""


RETRIEVE_MODEL = 'retrieve_model'
def retrieve_model(state: ResearchState):
    query = state['query']
    search_count = state['search_count']

    vector_store = get_vector_store()
    retrieved_docs = vector_store.similarity_search(query, k=search_count)

    return {'documents': retrieved_docs}


RANK_MODEL = 'rank_model'
def rank_model(state: ResearchState):
    query = state['query']
    documents = state['documents']

    formatted_prompt = RANKING_PROMPT.format(query=query, documents=documents)
    system_message = SystemMessage(content=formatted_prompt)

    response = llm.with_structured_output(RankList).invoke([system_message]+[HumanMessage(content='Rank the documents')])
    state['documents'] = [doc for i, doc in enumerate(documents) if response.ranks[i].relevance > .4]
    return state

    
WEB_MODEL = 'web_model'
def web_model(state: ResearchState):
    query = state['query']
    search_count = state['search_count']

    formatted_prompt = SEARCH_PROMPT.format(query=query)
    response = llm.invoke([SystemMessage(content=formatted_prompt)] + [HumanMessage(content=f"Turn the question into a search query")])
    
    tavily_search = TavilySearch(max_results=search_count, search_depth='advanced')
    search_result = tavily_search.invoke(response.content)
    documents = [
        Document(page_content=result['content'], metadata={'url': result['url'], 'title': result['title']}) 
        for result in search_result['results']
    ]

    return {'documents': documents}


def should_search(state: ResearchState):
    documents = state['documents']
    return END if len(documents) else WEB_MODEL


research_builder = StateGraph(ResearchState)

research_builder.add_node(RETRIEVE_MODEL, retrieve_model)
research_builder.add_node(RANK_MODEL, rank_model)
research_builder.add_node(WEB_MODEL, web_model)

research_builder.set_entry_point(RETRIEVE_MODEL)
research_builder.add_edge(RETRIEVE_MODEL, RANK_MODEL)
research_builder.add_conditional_edges(RANK_MODEL, should_search, [END, WEB_MODEL])
research_builder.add_edge(WEB_MODEL, END)

def get_research_graph():
    return research_builder.compile()


@tool
def research_tool(query: str, search_count=5):
    """Tool to make research based on provided query"""
    graph = get_research_graph()
    return graph.invoke({'query': query, 'search_count': search_count})