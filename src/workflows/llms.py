"""LLM and embedding configuration module.

Provides factory functions for getting LLM and embedding instances
based on environment configuration.
"""
from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from dotenv import load_dotenv

from src.lib.utils.config import ENV, ENVIRONMENTS, GOOGLE_API_KEY, OLLAMA_BASE_URL, OLLAMA_API_KEY


load_dotenv()


def get_llm(model: str = 'gpt-oss:20b-cloud', temperature: float = 0) -> ChatOllama:
    """Get LLM instance based on environment configuration.

    Args:
        model: Model name to use
        temperature: Sampling temperature for response generation

    Returns:
        ChatOllama LLM instance configured for environment

    Notes:
        - Uses cloud configuration for PRODUCTION and STAGING
        - Uses local Ollama for DEVELOPMENT and TESTING
    """
    config = {
        'model': model,
        'base_url': OLLAMA_BASE_URL,
        'temperature': temperature
    }

    if ENV in [ENVIRONMENTS.PRODUCTION, ENVIRONMENTS.STAGING]:
        config['cloud'] = True
        config['api_key'] = OLLAMA_API_KEY

    return ChatOllama(**config)


def get_embedding():
    """Get embedding model instance based on environment.

    Returns:
        Embedding model instance (Google or Ollama)

    Notes:
        - Uses Google Gemini embeddings for PRODUCTION and STAGING
        - Uses Ollama nomic-embed-text for DEVELOPMENT and TESTING
    """
    embedding = (
        GoogleGenerativeAIEmbeddings(model='models/gemini-embedding-001', google_api_key=GOOGLE_API_KEY)
        if ENV in [ENVIRONMENTS.PRODUCTION, ENVIRONMENTS.STAGING]
        else OllamaEmbeddings(model='nomic-embed-text', base_url=OLLAMA_BASE_URL)
    )
    return embedding
