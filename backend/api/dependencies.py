from functools import lru_cache

from config import settings
from ingestion.embedder import Embedder
from llm.ollama_client import OllamaClient
from retrieval.retriever import Retriever
from vector_store.chroma_store import ChromaVectorStore


@lru_cache(maxsize=1)
def get_embedder() -> Embedder:
    return Embedder(model_name=settings.EMBEDDING_MODEL)


@lru_cache(maxsize=1)
def get_vector_store() -> ChromaVectorStore:
    return ChromaVectorStore(
        persist_dir=settings.CHROMA_DIR,
        collection_name=settings.COLLECTION_NAME,
    )


@lru_cache(maxsize=1)
def get_retriever() -> Retriever:
    return Retriever(
        embedder=get_embedder(),
        vector_store=get_vector_store(),
    )


@lru_cache(maxsize=1)
def get_ollama_client() -> OllamaClient:
    return OllamaClient(
        base_url=settings.OLLAMA_BASE_URL,
        model=settings.OLLAMA_MODEL,
    )