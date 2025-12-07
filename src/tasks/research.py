from src.agents.researcher.research_graph import get_research_graph
from src.lib.utils.rag_pipeline import RAGPipeline

from src.config.queue import celery_app

research_graph = get_research_graph()

@celery_app.task
def research_topic(topic: str, depth: str = 'extremely basic'):
    research = research_graph.invoke({'topic': topic, 'depth': depth})
    rag_pipeline = RAGPipeline()
    doc_len = rag_pipeline.vectorize(research['documents'])
    return f"Research completed and {doc_len} documents vectorized."