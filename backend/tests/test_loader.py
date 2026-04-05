import pytest
from pathlib import Path
from ingestion.loader import DocumentLoader

def test_document_loader_txt(tmp_path):
    # Setup test file
    test_dir = tmp_path / "docs"
    test_dir.mkdir()
    test_file = test_dir / "sample.txt"
    test_content = "This is a sample document for testing the RAG system."
    test_file.write_text(test_content)

    loader = DocumentLoader()
    docs = loader.load_from_directory(test_dir)

    assert len(docs) == 1
    assert docs[0].filename == "sample.txt"
    assert docs[0].file_type == "txt"
    assert docs[0].content == test_content

def test_document_loader_skips_unsupported(tmp_path):
    test_dir = tmp_path / "docs"
    test_dir.mkdir()
    img_file = test_dir / "image.png"
    img_file.write_bytes(b"fake image data")

    loader = DocumentLoader()
    docs = loader.load_from_directory(test_dir)

    assert len(docs) == 0

def test_document_loader_missing_dir():
    loader = DocumentLoader()
    with pytest.raises(FileNotFoundError):
        loader.load_from_directory(Path("/non/existent/path"))
