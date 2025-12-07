from pymongo.database import Database
from langchain_core.documents import Document
import asyncio

from src.config.config import GOOGLE_COMPLIANCE_FOLDER_ID
from src.config.queue import celery_app

from src.lib.store.google_drive import GoogleDrive
from src.config.database import get_db
from src.lib.utils.logger import get_logger
from src.lib.utils.rag_pipeline import RAGPipeline

sync_logger = get_logger(name='KnowledgeSync')
rag_pipeline = RAGPipeline()

async def sync_compliance(db: Database):
    drive = GoogleDrive()
    documents = await rag_pipeline.list_outdated_knowledge(folder_id=GOOGLE_COMPLIANCE_FOLDER_ID, db=db, drive=drive)
    data = drive.download_multiple(documents, 4)

    for file_id, data in data.items():
        text = data['text']
        medadata = data['metadata']
        chunks = rag_pipeline.split_text(text=text)
        documents = [
            Document(
                page_content=c, 
                metadata={
                    'source': medadata['name'], 
                    'file_id': file_id, 
                    'modifiedAt': medadata['modifiedTime'], 
                    'category': 'compliance', 
                    'chunk':i
                    }
                ) 
            for i, c in enumerate(chunks)
        ]

        count = rag_pipeline.vectorize(documents)
        sync_logger.info(f"Vectorized: {count}")

    return documents


@celery_app.task(name='sync_knowledge')
def sync_knowledge():    
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        # If no loop is set for this thread (common in Celery), create a new one.
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    db = loop.run_until_complete(get_db())
    loop.run_until_complete(sync_compliance(db))

