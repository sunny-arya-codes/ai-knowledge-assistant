# vector_store/chroma_store.py
import logging
from pathlib import Path

import chromadb
from chromadb.config import Settings as ChromaSettings

from ingestion.chunker import Chunk

logger = logging.getLogger(__name__)


class ChromaVectorStore:
    def __init__(self, persist_dir: Path, collection_name: str):
        persist_dir.mkdir(parents=True, exist_ok=True)

        self._client = chromadb.PersistentClient(
            path=str(persist_dir),
            settings=ChromaSettings(anonymized_telemetry=False),
        )
        self._collection = self._client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"},  # normalized vectors → cosine
        )
        logger.info(
            "ChromaDB ready — collection: '%s', existing docs: %d",
            collection_name,
            self._collection.count(),
        )

    def add_chunks(self, chunks: list[Chunk], embeddings: list[list[float]]) -> None:
        if not chunks:
            logger.warning("No chunks to store.")
            return

        self._collection.upsert(  # add नहीं, upsert — re-ingest safe है
            ids=[f"{c.filename}__chunk_{c.chunk_index}" for c in chunks],
            documents=[c.content for c in chunks],
            embeddings=embeddings,
            metadatas=[
                {"filename": c.filename, "chunk_index": c.chunk_index}
                for c in chunks
            ],
        )
        logger.info("Stored %d chunks in ChromaDB.", len(chunks))

    def query(self, query_embedding: list[float], top_k: int = 5) -> list[dict]:
        results = self._collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            include=["documents", "metadatas", "distances"],
        )

        retrieved = []
        for doc, meta, dist in zip(
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0],
        ):
            retrieved.append(
                {
                    "content": doc,
                    "filename": meta["filename"],
                    "chunk_index": meta["chunk_index"],
                    "score": round(1.0 - dist, 4),  # cosine distance → similarity
                }
            )

        return retrieved

    def clear_collection(self) -> None:
        name = self._collection.name
        self._client.delete_collection(name)
        self._collection = self._client.create_collection(
            name=name,
            metadata={"hnsw:space": "cosine"},
        )
        logger.info("Collection '%s' cleared and recreated.", name)

    @property
    def count(self) -> int:
        return self._collection.count()