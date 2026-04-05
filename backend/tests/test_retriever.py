import pytest
from unittest.mock import MagicMock
from retrieval.retriever import Retriever

@pytest.fixture
def mock_embedder():
    embedder = MagicMock()
    embedder.embed_query.return_value = [0.1] * 384
    return embedder

@pytest.fixture
def mock_vector_store():
    store = MagicMock()
    store.query.return_value = [
        {"content": "This is chunk 1", "filename": "doc1.txt"},
        {"content": "This is chunk 2", "filename": "doc1.txt"},
        {"content": "This is chunk 3", "filename": "doc2.pdf"}
    ]
    return store

def test_retriever_query(mock_embedder, mock_vector_store):
    retriever = Retriever(embedder=mock_embedder, vector_store=mock_vector_store)
    chunks = retriever.retrieve("What is RAG?", top_k=3)
    
    mock_embedder.embed_query.assert_called_once_with("What is RAG?")
    mock_vector_store.query.assert_called_once_with([0.1] * 384, top_k=3)
    
    assert len(chunks) == 3
    assert chunks[0]["filename"] == "doc1.txt"

def test_retriever_build_context():
    retriever = Retriever(embedder=MagicMock(), vector_store=MagicMock())
    chunks = [
        {"content": "Test context 1", "filename": "file.txt"},
        {"content": "Test context 2", "filename": "file.txt"}
    ]
    context = retriever.build_context(chunks)
    
    assert "[1] (Source: file.txt)" in context
    assert "Test context 1" in context
    assert "[2] (Source: file.txt)" in context
    assert "Test context 2" in context

def test_retriever_unique_sources():
    retriever = Retriever(embedder=MagicMock(), vector_store=MagicMock())
    chunks = [
        {"content": "...", "filename": "docA.txt"},
        {"content": "...", "filename": "docB.pdf"},
        {"content": "...", "filename": "docA.txt"}
    ]
    sources = retriever.get_unique_sources(chunks)
    
    assert len(sources) == 2
    assert "docA.txt" in sources
    assert "docB.pdf" in sources
