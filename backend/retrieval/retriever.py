import logging

from ingestion.embedder import Embedder
from vector_store.chroma_store import ChromaVectorStore

logger = logging.getLogger(__name__)


class Retriever:
    def __init__(self, embedder: Embedder, vector_store: ChromaVectorStore):
        self._embedder = embedder
        self._vector_store = vector_store

    def retrieve(self, question: str, top_k: int = 5) -> list[dict]:
        query_embedding = self._embedder.embed_query(question)
        chunks = self._vector_store.query(query_embedding, top_k=top_k)
        logger.info(
            "Retrieved %d chunks for question: '%s...'",
            len(chunks),
            question[:60],
        )
        return chunks

    def build_context(self, chunks: list[dict]) -> str:
        parts = []
        for i, chunk in enumerate(chunks, start=1):
            parts.append(f"[{i}] (Source: {chunk['filename']})\n{chunk['content']}")
        return "\n\n---\n\n".join(parts)

    def get_unique_sources(self, chunks: list[dict]) -> list[str]:
        seen = set()
        sources = []
        for chunk in chunks:
            name = chunk["filename"]
            if name not in seen:
                seen.add(name)
                sources.append(name)
        return sources