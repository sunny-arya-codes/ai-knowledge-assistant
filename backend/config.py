# config.py — updated
from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    # Ingestion
    DOCS_DIR: Path = Path("documents")
    CHROMA_DIR: Path = Path("chroma_db")
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    CHUNK_SIZE: int = 500
    CHUNK_OVERLAP: int = 50
    COLLECTION_NAME: str = "knowledge_base"

    # LLM
    OLLAMA_BASE_URL: str = "http://ollama:11434"
    OLLAMA_MODEL: str = "llama3.2"

    class Config:
        env_file = ".env"


settings = Settings()