from dotenv import load_dotenv
from langchain_mongodb import MongoDBAtlasVectorSearch
from pymongo import MongoClient

from .config import MONGO_VECTOR_COLLECTION, MONGO_VECTOR_INDEX, VECTOR_URL, MONGO_DB
from .llms import get_embedding

load_dotenv()

def get_vector_store():
    client = MongoClient(VECTOR_URL)
    collection = client[MONGO_DB][MONGO_VECTOR_COLLECTION]
    embedding = get_embedding()

    vector_store = MongoDBAtlasVectorSearch(
        collection=collection,
        embedding=embedding,
        index_name=MONGO_VECTOR_INDEX,
        relevance_score_fn="cosine"
    )

    try:
        vector_store.create_vector_search_index(dimensions=3072)
    except Exception as e:
        print(f"⚠️ Skipping index creation: {e}")
        
    return vector_store
