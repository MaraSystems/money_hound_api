from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from uuid import uuid4
from pymongo.database import Database
from datetime import datetime

from ..store.google_drive import GoogleDrive
from src.config.config import MONGO_VECTOR_COLLECTION
from src.config.vector_store import get_vector_store
from src.lib.utils.logger import get_logger


class RAGPipeline():
    logger = get_logger('RAGPipeline')

    def split_text(self, text: str, chunk_size=1000, overlap=100):
        """Split text into chunks"""
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=overlap,
            separators=['\n\n', '\n', ' ', '']
        )
        return splitter.split_text(text)
    

    def vectorize(self, documents: list[Document]):
        vector_store = get_vector_store()
        ids = [str(uuid4()) for _ in range(len(documents))]
        vector_store.add_documents(documents=documents, ids=ids)
        return len(ids)
    

    async def list_outdated_knowledge(self, folder_id: str, db: Database, drive: GoogleDrive):
        knowledge_collection = db.knowledge
        vector_collection = db[MONGO_VECTOR_COLLECTION]

        docs = drive.list_documents(folder_id)
        document_list = []

        for doc in docs:
            file_id = doc['id']
            modifiedTime = datetime.fromisoformat(doc['modifiedTime']).replace(tzinfo=None)
            name = doc['name']

            document = await knowledge_collection.find_one({'file_id': file_id})
            if not document:
                await knowledge_collection.insert_one({'file_id': file_id, 'name': name, 'modifiedTime': modifiedTime})
                await vector_collection.delete_many({'file_id': file_id})
                document_list.append(file_id)
            
            outdated_doc = document and modifiedTime > document['modifiedTime'].replace(tzinfo=None)
            if outdated_doc:
                await knowledge_collection.update_one({'file_id': file_id}, {'$set': {'name': name, 'modifiedTime': modifiedTime}})
                await vector_collection.delete_many({'file_id': file_id})

                document_list.append(file_id)
        return document_list

    