import logging

from sentence_transformers import SentenceTransformer

from .chunker import Chunk

logger = logging.getLogger(__name__)


class Embedder:

    def __init__(self, model_name: str):
        logger.info("Loading embedding model: %s", model_name)
        self._model = SentenceTransformer(model_name)
        logger.info("Embedding model ready.")

    def embed_chunks(self, chunks: list[Chunk]) -> list[list[float]]:
        if not chunks:
            return []

        texts = [chunk.content for chunk in chunks]
        logger.info("Embedding %d chunks...", len(texts))

        embeddings = self._model.encode(
            texts,
            batch_size=32,
            show_progress_bar=True,
            normalize_embeddings=True,  
        )
        return embeddings.tolist()

    def embed_query(self, query: str) -> list[float]:
        embedding = self._model.encode(query, normalize_embeddings=True)
        return embedding.tolist()