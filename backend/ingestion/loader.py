import logging
from dataclasses import dataclass
from pathlib import Path

import fitz  

logger = logging.getLogger(__name__)


@dataclass
class Document:
    content: str
    filename: str
    file_type: str


class DocumentLoader:
    SUPPORTED_EXTENSIONS = {".pdf", ".txt"}

    def load_from_directory(self, directory: Path) -> list[Document]:
        if not directory.exists():
            raise FileNotFoundError(f"Documents directory not found: {directory}")

        documents = []
        for file_path in sorted(directory.iterdir()):
            if file_path.suffix.lower() not in self.SUPPORTED_EXTENSIONS:
                logger.warning("Skipping unsupported file: %s", file_path.name)
                continue
            try:
                doc = self._load_file(file_path)
                if doc and doc.content.strip():
                    documents.append(doc)
                    logger.info("Loaded: %s (%d chars)", file_path.name, len(doc.content))
                else:
                    logger.warning("Empty content, skipping: %s", file_path.name)
            except Exception as exc:
                logger.error("Failed to load %s: %s", file_path.name, exc)

        return documents

    def _load_file(self, file_path: Path) -> Document | None:
        match file_path.suffix.lower():
            case ".pdf":
                return self._load_pdf(file_path)
            case ".txt":
                return self._load_txt(file_path)
            case _:
                return None

    def _load_pdf(self, file_path: Path) -> Document:
        pages_text = []
        with fitz.open(file_path) as pdf:
            for page_num, page in enumerate(pdf, start=1): 
                text = page.get_text()
                if text.strip():
                    pages_text.append(text)
                else:
                    logger.debug("Page %d of %s has no text.", page_num, file_path.name)

        return Document(
            content="\n".join(pages_text).strip(),
            filename=file_path.name,
            file_type="pdf",
        )

    def _load_txt(self, file_path: Path) -> Document:
        content = file_path.read_text(encoding="utf-8")
        return Document(
            content=content.strip(),
            filename=file_path.name,
            file_type="txt",
        )