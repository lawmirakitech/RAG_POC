import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent

dotenv_path = BASE_DIR / ".env"

load_dotenv(dotenv_path=dotenv_path)

class Settings:

    #weaviate
    WEAVIATE_URL: str = os.getenv("WEAVIATE_URL")
    WEAVIATE_API_KEY: str = os.getenv("WEAVIATE_API_KEY")
    WEAVIATE_CLASS: str = "Documents7"
    
    # Provider configurations
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

    #tokenization
    MODEL_NAME = "BAAI/bge-large-en-v1.5"

    APP_NAME: str = "Chat Bot"
    APP_VERSION: str = "v1"

    #Note increasing it might take longer time to parse and ingest
    URL_PARSING_MAX_DEPT = 1
    EMBEDDING_MODEL = "BAAI/bge-large-en-v1.5"


settings = Settings()