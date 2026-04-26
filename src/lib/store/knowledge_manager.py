from langchain_chroma import Chroma
from chromadb.config import Settings
import chromadb
from langchain_core.tools import StructuredTool
from langchain_ollama import OllamaEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pandas import DataFrame
from langchain_core.documents import Document

from src.lib.store.google_drive import download, list_documents
from src.lib.utils.config import VECTOR_DIR
from src.lib.utils.logger import get_logger


class KnowledgeManager:
    """Manages vector storage for RAG-based knowledge retrieval.

    Handles ingestion, updating, and retrieval of documents from
    Chroma vector store. Supports syncing from Google Drive and
    ingesting from pandas DataFrames.
    """

    logger = get_logger('KnowledgeManager')

    def __init__(self, collection_name: str, embedding: OllamaEmbeddings, persistent_dir: str = VECTOR_DIR):
        """Initialize the knowledge manager with Chroma vector store.

        Args:
            collection_name: Name of the Chroma collection
            persistent_dir: Directory path for persistent storage
        """
        self.collection_name = collection_name
        self.embedding = embedding
        self.persistent_dir = persistent_dir

        self.client = chromadb.PersistentClient(
            path=self.persistent_dir,
            settings=Settings(
                allow_reset=True,
                anonymized_telemetry=False
            )
        )

        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"}
        )

        self.store = Chroma(
            collection_name=self.collection_name,
            embedding_function=self.embedding,
            persist_directory=self.persistent_dir,
            client=self.client
        )


    def split_text(self, text: str, chunk_size: int = 1000, overlap: int = 100) -> list:
        """Split text into overlapping chunks for vector embedding.

        Args:
            text: Text content to split
            chunk_size: Maximum characters per chunk
            overlap: Number of overlapping characters between chunks

        Returns:
            List of text chunks
        """
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=overlap,
            separators=['\n\n', '\n', ' ', '']
        )
        return splitter.split_text(text)


    def split_dataframe(self, df: DataFrame) -> list:
        """Convert DataFrame rows into document strings.

        Args:
            df: Pandas DataFrame to convert

        Returns:
            List of Document objects with row data as text
        """
        documents = []
        for _, row in df.iterrows():
            text = " | ".join(f'{col}:{row[col]}' for col in df.columns)
            documents.append(Document(text))

        return documents


    async def ingest_from_drive(self, folder_id: str):
        """Ingest all documents from a Google Drive folder.

        Args:
            folder_id: Google Drive folder ID
        """
        files = list_documents(folder_id)
        self.logger.info(f"Found {len(files)} files in folder {folder_id}")

        for file in files:
            await self.update_document(file['id'])
            self.logger.info(f"Ingested file {file['name']} with id {file['id']} into vector store")


    def ingest_from_dataframe(self, df: DataFrame, file_id: str):
        """Ingest data from a pandas DataFrame into the vector store.

        Args:
            df: DataFrame containing data to ingest
            file_id: Identifier for the data source
        """
        documents = self.split_dataframe(df)
        chunks = self.split_text("\n".join([doc.page_content for doc in documents]))
        self.delete_document(file_id)

        self.store.add_texts(
            texts=chunks,
            metadatas=[{"file_id": file_id}] * len(chunks),
            ids=[f"{file_id}_{i}" for i in range(len(chunks))]
        )
        self.logger.info(f"Ingested dataframe with id {file_id} into vector store")


    async def update_document(self, file_id: str):
        """Download and ingest a document from Google Drive.

        Deletes any existing version before adding the updated content.

        Args:
            file_id: Google Drive file ID
        """
        text, metadata = await download(file_id)
        chunks = self.split_text(text)
        self.delete_document(file_id)

        self.store.add_texts(
            texts=chunks,
            metadatas=[{**metadata, "file_id": file_id}] * len(chunks),
            ids=[f"{file_id}_{i}" for i in range(len(chunks))]
        )
        self.logger.info(f"Updated document with id {file_id} in vector store")


    def get_file(self, file_id: str) -> dict:
        """Retrieve all chunks associated with a file ID.

        Args:
            file_id: File identifier to search for

        Returns:
            Dictionary with ids, metadatas, and documents
        """
        results = self.collection.get(
            where={"file_id": {"$eq": file_id}}
        )
        return results


    def delete_document(self, file_id: str):
        """Delete all chunks associated with a file ID.

        Args:
            file_id: File identifier to delete
        """
        results = self.get_file(file_id)
        if results['ids']:
            self.collection.delete(ids=results['ids'])

        self.logger.info(f"Deleted document with id {file_id} from vector store")


    def list_outdated_documents(self, folder_id: str) -> list:
        """Find documents in Drive that are newer than stored versions.

        Args:
            folder_id: Google Drive folder ID

        Returns:
            List of file IDs that need updating
        """
        docs = list_documents(folder_id)
        outdated_docs = []

        for doc in docs:
            file_id = doc['id']
            modifiedTime = doc['modifiedTime']

            stored_doc = self.collection.get(where={"file_id": {"$eq": file_id}})
            if not stored_doc['ids']:
                outdated_docs.append(file_id)
                continue

            stored_modifiedTime = stored_doc['metadatas'][0]['modifiedTime']
            if modifiedTime > stored_modifiedTime:
                outdated_docs.append(file_id)

        return outdated_docs


    async def sync_drive(self, folder_id: str):
        """Sync outdated documents from Google Drive to vector store.

        Args:
            folder_id: Google Drive folder ID
        """
        files = self.list_outdated_documents(folder_id)
        self.logger.info(f"Found {len(files)} outdated files in folder {folder_id}")

        for file in files:
            await self.update_document(file['id'])
            self.logger.info(f"Ingested file {file['name']} with id {file['id']} into vector store")


    def retrieve(self, query: str, search_count: int = 3) -> list:
        """Retrieve relevant documents from the vector store.

        Uses MMR (Maximum Marginal Relevance) search for diversity.

        Args:
            query: Search query string
            search_count: Number of results to return

        Returns:
            List of relevant Document objects
        """
        retriever = self.store.as_retriever(search_type='mmr', search_kwargs={'k': search_count})
        data = retriever.invoke(query)
        return data


    def retrieve_tool(self) -> StructuredTool:
        """Create a LangChain tool for knowledge retrieval.

        Returns:
            StructuredTool for querying the vector store
        """
        return StructuredTool.from_function(
            name='knowledge_retriever',
            description=(
                "Used to extract knowledge from the vector store"
                "Can be used to extract transaction histories"
            ),
            func=lambda query, search_count=None: self.retrieve(query=query, search_count=search_count)
        )