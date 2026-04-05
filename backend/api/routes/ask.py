# api/routes/ask.py
import json
import logging
from collections.abc import AsyncGenerator

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse

from api.dependencies import get_ollama_client, get_retriever
from api.schemas import AskRequest, AskResponse
from llm.ollama_client import OllamaClient
from retrieval.retriever import Retriever

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ask", tags=["QnA"])


@router.post(
    "",
    response_model=AskResponse,
    summary="Ask a question and get a complete answer",
)
def ask(
    body: AskRequest,
    retriever: Retriever = Depends(get_retriever),
    llm: OllamaClient = Depends(get_ollama_client),
) -> AskResponse:
    chunks = retriever.retrieve(body.question)

    if not chunks:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No relevant documents found for this question.",
        )

    context = retriever.build_context(chunks)
    sources = retriever.get_unique_sources(chunks)

    try:
        answer = llm.generate(question=body.question, context=context)
    except Exception as exc:
        logger.error("LLM generation failed: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="LLM service unavailable. Is Ollama running?",
        ) from exc

    return AskResponse(answer=answer, sources=sources)


@router.post(
    "/stream",
    summary="Ask a question and receive a streaming SSE response",
)
def ask_stream(
    body: AskRequest,
    retriever: Retriever = Depends(get_retriever),
    llm: OllamaClient = Depends(get_ollama_client),
) -> StreamingResponse:
    chunks = retriever.retrieve(body.question)

    if not chunks:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No relevant documents found for this question.",
        )

    context = retriever.build_context(chunks)
    sources = retriever.get_unique_sources(chunks)

    def event_generator() -> AsyncGenerator:
        try:
            for token in llm.stream(question=body.question, context=context):
                # SSE format: data: <payload>\n\n
                yield f"data: {json.dumps({'token': token})}\n\n"

            # Stream खत्म — sources भेजो
            yield f"data: {json.dumps({'done': True, 'sources': sources})}\n\n"

        except Exception as exc:
            logger.error("Streaming error: %s", exc)
            yield f"data: {json.dumps({'error': str(exc)})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",   # nginx buffering बंद
            "Connection": "keep-alive",
        },
    )