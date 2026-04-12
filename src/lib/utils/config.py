"""Application configuration module.

Loads environment variables and provides centralized configuration
for the Busense API application.
"""
from pathlib import Path
from dotenv import load_dotenv
from enum import StrEnum
import os

load_dotenv()

class ENVIRONMENTS(StrEnum):
    """Enumeration of supported deployment environments.

    Members:
        DEVELOPMENT: Local development environment
        STAGING: Pre-production staging environment
        TESTING: Automated testing environment
        PRODUCTION: Live production environment
    """
    DEVELOPMENT = "DEVELOPMENT"
    STAGING = "STAGING"
    TESTING = "TESTING"
    PRODUCTION = "PRODUCTION"

# Application settings
APP_NAME = os.getenv('APP_NAME', 'API')
ENV = os.getenv('ENV', ENVIRONMENTS.DEVELOPMENT)
CLEAN = bool(os.getenv('CLEAN', False))

# Authentication settings
SECRET = os.getenv('SECRET', 'secret')
CACHE_TTL = int(os.getenv('CACHE_TTL', 3600))
ALGORITHM = os.getenv('ALGORITHM', 'HS256')

# Database connections
MONGO_URL = os.getenv('MONGO_URL')
REDIS_URL = os.getenv('REDIS_URL')

# Email configuration
DEFAULT_EMAIL = os.getenv('DEFAULT_EMAIL')
MAIL_USER = os.getenv('MAIL_USER')
MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')

# Pagination and rate limiting
PAGE_LIMIT = int(os.getenv('PAGE_LIMIT', 10))
REQUEST_LIMIT = int(os.getenv('REQUEST_LIMIT', 5))

# Base directory paths
BASE_DIR = Path(__file__).parent.parent.parent.resolve()
GOOGLE_APPLICATION_CREDENTIALS = os.path.join(BASE_DIR, os.getenv('GOOGLE_APPLICATION_CREDENTIALS', ''))
GOOGLE_PROJECT_ID = os.getenv('GOOGLE_PROJECT_ID')
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
GOOGLE_FOLDER_ID = os.getenv('GOOGLE_FOLDER_ID')
LANGSMITH_API_KEY = os.getenv('LANGSMITH_API_KEY')

# Data and storage paths
DATA_URL = os.getenv('DATA_URL', None)
UPLOAD_PATH = os.path.join(BASE_DIR, f"uploads_{ENV}")
DATA_DIR = os.path.join(BASE_DIR, "datasets")
VECTOR_DIR = os.path.join(BASE_DIR, "vectors")
MODEL_DIR = os.path.join(BASE_DIR, "models")

# LLM configuration
OLLAMA_BASE_URL = os.getenv('OLLAMA_BASE_URL')
OLLAMA_API_KEY = os.getenv('OLLAMA_API_KEY')

# Background task and upload settings
EXTERNAL_BACKGROUND = bool(int(os.getenv('EXTERNAL_BACKGROUND', 0)))
UPLOAD_LIMIT = int(os.getenv('UPLOAD_LIMIT', 11331600))
UPLOAD_TYPES = {'image/jpeg', 'image/png', 'image/webp', 'image/gif', 'application/pdf'}