import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.dependencies import get_embedder, get_vector_store
from api.routes import ask

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Warming up embedder and vector store...")
    get_embedder()
    get_vector_store()
    logger.info("Ready to serve requests.")
    yield
    logger.info("Shutting down.")


app = FastAPI(
    title="AI Knowledge Assistant",
    description="RAG-based document Q&A system",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["POST"],
    allow_headers=["*"],
)

app.include_router(ask.router)


@app.get("/health", tags=["Health"])
def health_check() -> dict:
    return {"status": "ok"}