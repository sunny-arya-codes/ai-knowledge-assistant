# ingestion/pipeline.py
import logging
from pathlib import Path

from config import settings
from .chunker import TextChunker
from .embedder import Embedder
from .loader import DocumentLoader
from vector_store.chroma_store import ChromaVectorStore

logger = logging.getLogger(__name__)


class IngestionPipeline:
    def __init__(self):
        self.loader = DocumentLoader()
        self.chunker = TextChunker(
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP,
        )
        self.embedder = Embedder(model_name=settings.EMBEDDING_MODEL)
        self.vector_store = ChromaVectorStore(
            persist_dir=settings.CHROMA_DIR,
            collection_name=settings.COLLECTION_NAME,
        )

    def run(self, docs_dir: Path | None = None, clear_existing: bool = False) -> dict:
        directory = docs_dir or settings.DOCS_DIR

        if clear_existing:
            logger.info("Clearing existing collection...")
            self.vector_store.clear_collection()

        logger.info("=== Ingestion Start: %s ===", directory)

        # Step 1 — Load
        documents = self.loader.load_from_directory(directory)
        if not documents:
            logger.warning("No documents found in: %s", directory)
            return {"status": "skipped", "reason": "no documents found"}

        # Step 2 — Chunk
        chunks = self.chunker.chunk_documents(documents)

        # Step 3 — Embed
        embeddings = self.embedder.embed_chunks(chunks)

        # Step 4 — Store
        self.vector_store.add_chunks(chunks, embeddings)

        summary = {
            "status": "success",
            "documents_loaded": len(documents),
            "chunks_created": len(chunks),
            "total_stored": self.vector_store.count,
        }
        logger.info("=== Ingestion Complete: %s ===", summary)
        return summary