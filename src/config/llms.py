from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from dotenv import load_dotenv

from src.config.config import ENV, ENVIRONMENTS, OLLAMA_BASE_URL

load_dotenv()


def get_llm():
    llm = ChatOllama(model='qwen2.5:7b-instruct', base_url=OLLAMA_BASE_URL) if ENV not in [ENVIRONMENTS.PRODUCTION, ENVIRONMENTS.STAGING] else ChatOpenAI(model="gpt-4o-mini", temperature=0)
    return llm

def get_embedding():
    return OpenAIEmbeddings(model="text-embedding-3-large")
