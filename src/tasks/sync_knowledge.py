import asyncio

from src.lib.utils.config import GOOGLE_FOLDER_ID
from src.lib.store.knowledge_manager import KnowledgeManager


def sync_knowledge_task():
    """Sync company documents from Google Drive to the vector store.

    Initializes the KnowledgeManager and syncs all outdated documents
    from the configured Google Drive folder. Runs as a Celery task
    for background execution.
    """
    knowledge_manager = KnowledgeManager('company_docs')
    asyncio.run(knowledge_manager.sync_drive(GOOGLE_FOLDER_ID))
