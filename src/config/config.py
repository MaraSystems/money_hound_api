from dotenv import load_dotenv
from enum import StrEnum
import os

load_dotenv()

APP_NAME = os.getenv('APP_NAME', 'API')
ENV = os.getenv('ENV', 'test')

SECRET = os.getenv('SECRET', 'secret')
CACHE_TTL = int(os.getenv('CACHE_TTL', 3600))
ALGORITHM = os.getenv('ALGORITHM', 'HS256')

MONGO_URL = os.getenv('MONGO_URL')
MONGO_DB = os.getenv('MONGO_DB', 'random')

VECTOR_URL = os.getenv('VECTOR_URL')
MONGO_VECTOR_COLLECTION = os.getenv('MONGO_VECTOR_COLLECTION')
MONGO_VECTOR_INDEX = os.getenv('MONGO_VECTOR_INDEX')

REDIS_URL = os.getenv('REDIS_URL')

DEFAULT_EMAIL = os.getenv('DEFAULT_EMAIL')

MAIL_USER = os.getenv('MAIL_USER')
MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')

PAGE_LIMIT = int(os.getenv('PAGE_LIMIT', 10))
REQUEST_LIMIT = int(os.getenv('REQUEST_LIMIT', 5))

GOOGLE_APPLICATION_CREDENTIALS = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
GOOGLE_PROJECT_ID = os.getenv('GOOGLE_PROJECT_ID')
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
LANGSMITH_API_KEY = os.getenv('LANGSMITH_API_KEY')
GOOGLE_DOC_ID = os.getenv('GOOGLE_DOC_ID')

UPLOAD_PATH = f"{os.getenv('UPLOAD_PATH')}_{ENV}"
DATA_URL = os.getenv('DATA_URL', None)
BASE_DIR = os.path.dirname(__file__)  
DATA_DIR = os.path.join(BASE_DIR, "../../datasets")
DOCUMENT_DIR = os.path.join(BASE_DIR, "../documents")
MODEL_DIR = os.path.join(BASE_DIR, "../models")

OLLAMA_BASE_URL = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')

GOOGLE_COMPLIANCE_FOLDER_ID = os.getenv('GOOGLE_COMPLIANCE_FOLDER_ID')

class ENVIRONMENTS(StrEnum):
    DEVELOPMENT = "DEVELOPMENT"
    STAGING = "STAGING"
    TESTING = "TESTING"
    PRODUCTION = "PRODUCTION"
