# api/schemas.py
from pydantic import BaseModel, Field


class AskRequest(BaseModel):
    question: str


class AskResponse(BaseModel):
    answer: str
    sources: list[str]  # unique filenames only


class RetrievedChunk(BaseModel):
    content: str
    filename: str
    chunk_index: int
    score: float