# AI Knowledge Assistant (RAG System)

A Retrieval-Augmented Generation (RAG) system built to ingest your documents and answer questions contextually using local LLMs.

## Project Overview

The **AI Knowledge Assistant** empowers users to extract insights from personal or organizational documents (`.pdf`, `.txt`) completely offline and privately. By orchestrating robust chunking, semantic vector embeddings, and LLM generative logic powered by Ollama, it maintains a pure self-hosted AI architecture without relying on external APIs.

The system streams responses in real-time, reducing perceived latency, while consistently citing the exact document sources.

## Architecture

```mermaid
flowchart TD
    subgraph Frontend [Next.js Dashboard]
        UI([User Interface])
        API_Client([API Hooks])
    end

    subgraph Backend [FastAPI Application]
        Ingestion([Document Ingestion / Chunking])
        Retriever([Semantic Retriever])
        Ask_Route([/ask & /ask/stream Router])
    end
    
    subgraph Data [Storage Layer]
        Docs[(Local Documents)]
        Chroma[(ChromaDB Vector Store)]
    end
    
    subgraph LLM [Local Model Provider]
        Ollama((Ollama Server))
        Model[(llama3.2)]
    end

    %% Flow
    Docs -->|Raw Text/PDFs| Ingestion
    Ingestion -->|Embeddings| Chroma
    UI -->|Question| API_Client
    API_Client -->|POST /ask/stream| Ask_Route
    Ask_Route -->|Query| Retriever
    Retriever <-->|Fetch Top-K Context| Chroma
    Ask_Route -->|Context + Query| Ollama
    Ollama -->|Stream Tokens| Ask_Route
    Ask_Route -->|SSE Stream| UI
```

## Tech Stack

- **Backend:** Python, FastAPI, Contextual Generators (Async).
- **Vector Database:** ChromaDB (persistent local storage).
- **LLM Engine:** Ollama providing Llama3.2 (`11434`).
- **Embeddings:** HuggingFace `sentence-transformers` (`all-MiniLM-L6-v2`).
- **Frontend:** Next.js, React, Tailwind CSS.
- **Containerization:** Docker & Docker Compose.

## Setup & Execution

### Prerequisites
- Docker Engine & Docker Compose V2 (`docker compose`) installed.

### Quick Start Guide

**1. Clone the repository:**
```bash
git clone <repository_url>
cd ai-knowledge-assistant
```

**2. Start the services:**
```bash
docker compose up --build -d
```
*(Note: It may take a few minutes for the companion container to automatically pull the `llama3.2` model on the first run.)*

**3. Add your context documents:**
Copy your `.pdf` or `.txt` files into the local documents folder:
```bash
cp /path/to/your/files/* ./backend/documents/
```

**4. Ingest context into the Vector Store:**
Run the ingestion pipeline locally within the container:
```bash
docker compose exec backend python ingest.py
```

**5. Access the Knowledge Assistant:**
Open your browser and navigate to: **http://localhost:3000**

## API Documentation

### 1. `POST /ask`
Synchronous question-answering. Wait for the full completion.

**Request:**
```json
{
  "question": "What is the core topic of the documents?"
}
```

**Response:**
```json
{
  "answer": "The documents primarily discuss the implementation of distributed systems...",
  "sources": ["overview.pdf", "notes.txt"]
}
```
*Curl Example:*
```bash
curl -X POST "http://localhost:8000/ask" -H "Content-Type: application/json" -d '{"question":"Explain the architecture."}'
```

### 2. `POST /ask/stream`
Token-by-token streaming generator using Server-Sent Events (SSE).

**Request:** Same payload.
**Response Stream (SSE format):**
```text
data: {"token": "The"}
data: {"token": " architecture"}
data: {"token": " is"}
...
data: {"done": true, "sources": ["docs.txt"]}
```

## Testing

A `pytest` suite covers unit logic. Run this inside the backend container or locally:

```bash
cd backend
uv run pytest
```

## Design Decisions
- **Async Streaming:** Uses `httpx.AsyncClient` in FastAPI to prevent blocking the ASGI event loop.
- **Data Privacy:** Runs a completely offline Ollama instance eliminating external API telemetry.
- **Zero Cold-Starts:** Pre-loads ML embeddings and ChromaDB layers during FastAPI lifespan boot, yielding instant first-byte responses.

## Limitations
- **Basic Chunking:** Relies on hard character limits rather than intelligent semantic splitters.
- **Hardware Bottlenecks:** Single-node local inference restricts parallel/concurrent user throughput.

## Future Improvements
- Switch to Recursive / Markdown-aware document chunking.
- Implement explicit metadata filtering in ChromaDB.
- Add conversational memory (Redis) for multi-turn chat interactions.
