import logging
from dataclasses import dataclass

from langchain_text_splitters import RecursiveCharacterTextSplitter

from .loader import Document

logger = logging.getLogger(__name__)


@dataclass
class Chunk:
    content: str
    filename: str
    chunk_index: int


class TextChunker:

    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50):
        self._splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", ". ", " ", ""],
            length_function=len,
        )
        logger.info(
            "Chunker initialized — size=%d, overlap=%d", chunk_size, chunk_overlap
        )

    def chunk_documents(self, documents: list[Document]) -> list[Chunk]:
        all_chunks: list[Chunk] = []

        for doc in documents:
            raw_chunks = self._splitter.split_text(doc.content)
            doc_chunks = [
                Chunk(
                    content=text.strip(),
                    filename=doc.filename,
                    chunk_index=idx,
                )
                for idx, text in enumerate(raw_chunks)
                if text.strip()
            ]
            logger.info("%s → %d chunks", doc.filename, len(doc_chunks))
            all_chunks.extend(doc_chunks)

        return all_chunks